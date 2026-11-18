import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str
    QDRANT_TIMEOUT: int = 10

    # Redis is optional: leave REDIS_HOST empty (or unreachable) to disable caching.
    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = ""  # e.g. a Render Key Value internal URL; overrides host/port

    CORS_ORIGIN: str = ""

    # Must be the same model the scraper used to build the collection.
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_CACHE_DIR: str = "/app/models"
    EMBEDDING_THREADS: int | None = 1

    SEARCH_SCORE_THRESHOLD: float = 0.35
    SEARCH_LIMIT: int = 50


# For production: load from environment variables (Render sets these)
# For local dev: load from .env.dev if environment variable not set
_env = os.getenv("ENVIRONMENT", "dev")
if not os.getenv("QDRANT_URL"):
    load_dotenv(Path(__file__).resolve().parent.parent.parent / f".env.{_env}")

settings = Settings()
