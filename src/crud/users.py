from enums import UserRole
from logger import GGLogger
from models import ClientUser
from schemas.client_users import ClientUserCreate, ClientUserInDB
from gg_exceptions.client_users import UserNotFound

logger = GGLogger(__name__)

def get_user_by_username(db, username) -> ClientUser:
    client_user =  db.query(ClientUser).filter(ClientUser.username == username).first()
    if not client_user:
        logger.warning(f'User not found: {username}')
        raise UserNotFound
    logger.info(f'Retrieved User: {client_user.username}')
    return client_user


def create_user(db, user: ClientUserCreate):
    user = user.to_orm(ClientUser)
    db.add(user)
    db.commit()
    logger.info(f'Created User: {user.username}')

def update_password(db, username, password):
    client_user =  get_user_by_username(db, username)
    client_user.hashed_password = password
    db.commit()
    logger.info(f"Password Changed Successfully")

def update_role(db, username, role: UserRole):
    client_user =  get_user_by_username(db, username)
    if client_user.role != role:
        client_user.role = role
        db.commit()
        logger.info(f"Role Changed Successfully")

