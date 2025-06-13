from datetime import datetime
from enums import UserRole
from pydantic import BaseModel, SecretStr

# Base model with common attributes
class ClientUserBase(BaseModel):
    username: str

    class Config:
        from_attributes = True

# Authentication-related schemas
class ClientUserAuth(ClientUserBase):
    password: SecretStr

# Internal creation schema
class ClientUserCreate(ClientUserBase):
    id: str
    hashed_password: str
    role: UserRole

# Response schemas
class ClientUserResponse(ClientUserBase):
    id: str
    role: UserRole

# DB schema (internal use only)
class ClientUserInDB(ClientUserResponse):
    hashed_password: str
    created_at: datetime
    updated_at: datetime