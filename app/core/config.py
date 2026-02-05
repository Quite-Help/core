import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str


settings = Settings(
    DATABASE_URL=os.environ["DATABASE_URL"],
    JWT_SECRET=os.environ["JWT_SECRET"],
    JWT_ALGORITHM=os.environ["JWT_ALGORITHM"],
)
