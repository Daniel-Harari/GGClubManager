from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


class PGSettings(BaseSettings):
    pg_user: str
    pg_password: SecretStr
    pg_host: str
    pg_db: str
    pg_port: int = 5432


    @property
    def database_url(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_password.get_secret_value()}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


pg_settings = PGSettings()
engine = create_engine(pg_settings.database_url)
Base = declarative_base()
Base.__table_args__ = {"schema": "sheep_it"}
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
