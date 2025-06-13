import hashlib
from datetime import datetime, UTC
from functools import wraps
from typing import List, Callable

from dotenv import load_dotenv
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_cache.decorator import cache
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session

from crud.users import get_user_by_username
from consts import CURRENT_USER_CACHE_TTL
from gg_exceptions.auth import AuthenticationError, AuthNotProvided, TokenExpired
from db import get_db
from schemas.client_users import UserRole, ClientUserResponse
from logger import GGLogger


load_dotenv()
logger = GGLogger(__name__)


class AuthSettings(BaseSettings):
    auth_secret_key: str
    auth_algorithm: str
    access_token_expire_minutes: int


auth_settings = AuthSettings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="Bearer Token")


def create_access_token(user: ClientUserResponse) -> str:
    to_encode = {"username": user.username, "role": user.role.name, "id": user.id, "exp":
        int(datetime.now(UTC).timestamp() + auth_settings.access_token_expire_minutes * 60)
}
    encoded_jwt = jwt.encode(to_encode, auth_settings.auth_secret_key, algorithm=auth_settings.auth_algorithm)
    return encoded_jwt


def auth_key_builder(func, namespace: str, *args, **kwargs):
    # We'll use the first argument as our token_hash
    if args:
        return f"{namespace}:{args[0]}"
    return f"{namespace}:default"

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ClientUserResponse:
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    @cache(expire=CURRENT_USER_CACHE_TTL, namespace="auth", key_builder=auth_key_builder)
    async def get_cached_user(token_hash: str) -> dict:
        logger.info(f"Getting current user from DB")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, auth_settings.auth_secret_key, algorithms=[auth_settings.auth_algorithm])
            username: str = payload.get("username")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = ClientUserResponse.model_validate(get_user_by_username(db, username))
        if user is None:
            raise credentials_exception
        return user.model_dump()  # Convert to dict for caching

    cached_data = await get_cached_user(token_hash)
    return ClientUserResponse.model_validate(cached_data)  # Convert back to a Pydantic model


def check_roles(allowed_roles: List[UserRole]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError

    return user

def verify_token(token: str):
    if not token:
        raise AuthNotProvided
    # Extract token from "Bearer <token>"
    token = token.split(" ")[1] if token.startswith("Bearer ") else token

    # Decode and verify token
    try:
        jwt.decode(
            token,
            auth_settings.auth_secret_key,
            algorithms=[auth_settings.auth_algorithm]
        )
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise TokenExpired
    return True


def is_downline(username_param: str = 'username'):
    """
    Decorator to check if target username belongs to a downline of current user.

    Args:
        username_param: The parameter name in the decorated function that contains the target username
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            # Get the target username from kwargs or route parameters
            target_username = kwargs.get(username_param)
            if not target_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required parameter: {username_param}"
                )

            # Get target user from database
            target_user = await get_user_by_username(target_username)


            # Check if target user is a downline
            is_downline_user = await is_downline(
                current_user_role=current_user.role,
                target_user_role=target_user.role,
                target_parent_id=target_user.parent_id,
                current_user_id=current_user.id
            )

            if not is_downline_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. User is not in your downline"
                )

            # Add target_user to kwargs for convenience
            kwargs['target_user'] = target_user
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
