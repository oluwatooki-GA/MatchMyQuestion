from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os


class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str

    REDIS_HOST: str
    REDIS_PORT: str | int
    CORS_ORIGIN: str

    @classmethod
    def load(cls, environment: str = "dev"):
        env_path = Path(__file__).resolve().parent.parent.parent / f".env.{environment}"
        load_dotenv(env_path)
        return cls()


# For production: load from environment variables (Render sets these)
# For local dev: load from .env.dev if environment variable not set
_env = os.getenv("ENVIRONMENT", "dev")
if not os.getenv("QDRANT_URL"):
    load_dotenv(Path(__file__).resolve().parent.parent.parent / f".env.{_env}")

settings = Settings()
