import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TRANSCRIPTION_DIRECTORY: str = "transcriptions"
    GPT_API_KEY: str
    BASE_DIR: str
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)


def get_settings() -> Settings:
    return Settings()
