from fastapi import Depends

from core.settings.config import get_settings
from core.services.transcriber import TranscriptionService

from loguru import logger


def get_api_key() -> str:
    """
    Retrieve the GPT API key from the settings.

    Returns:
        str: The GPT API key.
    """
    settings = get_settings()
    return settings.GPT_API_KEY


def get_transcription_service(api_key: str = Depends(get_api_key)) -> TranscriptionService:
    """
    Initialize and return an instance of TranscriptionService.

    Args:
        api_key (str): The API key for the transcription service, injected by FastAPI's dependency system.

    Returns:
        TranscriptionService: An instance of the TranscriptionService class.

    """
    try:
        settings = get_settings()
        return TranscriptionService(api_key, settings.TRANSCRIPTION_DIRECTORY)
    except Exception as e:
        logger.error(f"Error initializing TranscriptionService: {e}")
