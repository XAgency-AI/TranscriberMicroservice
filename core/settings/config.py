from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TRANSCRIPTION_DIRECTORY: str = "transcriptions"
    GPT_API_KEY: str
    BASE_DIR: str


def get_settings() -> Settings:
    return Settings()
