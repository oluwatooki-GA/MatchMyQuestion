from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str | int
    DATABASE_PASSWORD: str
    DATABASE_USERNAME: str
    DATABASE_NAME: str

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str

    class Config:
        env_file = ''

    @classmethod
    def load_environment(cls, environment: str = "dev"):
        env_path = Path(__file__).resolve().parent.parent.parent / f".env.{environment}"
        if not env_path.exists():
            raise FileNotFoundError(f"Environment file {env_path} does not exist!")
        return cls(_env_file=env_path)
