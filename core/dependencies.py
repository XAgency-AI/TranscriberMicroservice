from fastapi import Depends

from core.config import settings
from core.services.transcriber import TranscriptionService


def get_api_key() -> str:
    return settings.GPT_API_KEY


def get_transcription_service(api_key: str = Depends(get_api_key)) -> TranscriptionService:
    return TranscriptionService(api_key, settings.TRANSCRIPTION_DIRECTORY)
