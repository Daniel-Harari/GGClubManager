from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from crud.players import get_player_by_username
from crud.users import get_user_by_username, create_user, update_password
from db import get_db
from enums import UserRole
from gg_exceptions.auth import AuthenticationError
from gg_exceptions.client_users import UserNotFound
from gg_exceptions.players import PlayerNotFound
from schemas.auth import Token
from schemas.client_users import ClientUserCreate, ClientUserAuth, ClientUserResponse
from utils.auth_utils import create_access_token, pwd_context, authenticate_user, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=Token,
             summary="Login endpoint for the API",
             description="Login endpoint for the API. Returns an access token and user data.")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = ClientUserResponse.model_validate(user)
    # Create an access token
    access_token = create_access_token(user)

    return Token(access_token=access_token, token_type="bearer")

@router.post("/register")
async def register(
        user_data: ClientUserAuth,
        db: Session = Depends(get_db)
):
    try:
        existing_user = get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
    except UserNotFound:
        pass

    try:
        player = get_player_by_username(db, user_data.username)
    except PlayerNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player not found in club"
        )

    hashed_password = pwd_context.hash(user_data.password.get_secret_value())
    new_user = ClientUserCreate(
        id=str(player.id),
        username=str(player.username),
        hashed_password=hashed_password,
        role = UserRole(player.role)
    )
    create_user(db, new_user)
    return {"message": "User created successfully"}


@router.post("/change_password")
async def change_password(
        user_data: ClientUserAuth,
        db: Session = Depends(get_db),
        current_user: ClientUserResponse = Depends(get_current_user)
):
    hashed_password = pwd_context.hash(user_data.password.get_secret_value())
    update_password(db, current_user.username, hashed_password)
    return {"message": "User created successfully"}