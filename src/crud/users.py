from logger import GGLogger
from models import ClientUser
from schemas.client_users import ClientUserCreate, ClientUserInDB
from gg_exceptions.client_users import UserNotFound

logger = GGLogger(__name__)

def get_user_by_username(db, username) -> ClientUserInDB:
    client_user =  db.query(ClientUser).filter(ClientUser.username == username).first()
    if not client_user:
        logger.warning(f'User not found: {username}')
        raise UserNotFound
    logger.info(f'Retrieved User: {client_user.username}')
    return ClientUserInDB.model_validate(client_user)


def create_user(db, user: ClientUserCreate):
    user = ClientUser(**user.model_dump())
    db.add(user)
    db.commit()
    logger.info(f'Created User: {user.username}')
