from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv


class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str

    @classmethod
    def load(cls, environment: str = "dev"):
        env_path = Path(__file__).resolve().parent.parent.parent / f".env.{environment}"
        load_dotenv(env_path)
        return cls()
