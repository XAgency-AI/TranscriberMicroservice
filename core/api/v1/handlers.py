import mimetypes
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from loguru import logger

from core.services.transcriber import TranscriptionService
from core.settings.dependencies import get_transcription_service


router = APIRouter(tags=['Transcriptions'])


@router.post("/transcribe/")
async def create_transcription(
    file: UploadFile = File(...),
    transcription_service: TranscriptionService = Depends(get_transcription_service)
) -> dict:
    """
    Endpoint to create a transcription from an uploaded audio or video file.

    Args:
        file (UploadFile): The uploaded file to transcribe.
        transcription_service (TranscriptionService): The transcription service dependency.

    Returns:
        dict: A dictionary containing the transcription and timestamps.

    Raises:
        HTTPException: If the file type is unsupported or an error occurs during transcription.
    """
    try:
        logger.info(f"Received file for transcription: {file.filename}")
        content = await file.read()
        mime_type, _ = mimetypes.guess_type(file.filename)

        if mime_type not in ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'video/mp4', 'audio/flac', 'audio/mp4']:
            logger.error(f"Unsupported file type: {mime_type}")
            raise HTTPException(status_code=400, detail="Unsupported file type")

        transcription_result = transcription_service.transcribe_media_content(
            content=content, filename=file.filename,
        )

        if not isinstance(transcription_result, dict):
            logger.error(f"Invalid transcription result type: {type(transcription_result)}")
            raise HTTPException(status_code=500, detail="Transcription result is not a valid dictionary")

        logger.info(f"Transcription completed for file: {file.filename}")
        return transcription_result
    except Exception as e:
        logger.error(f"An error occurred during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")

@router.post("/transcribe/youtube")
async def transcribe_youtube_video(
    url: str,
    return_only_vtt_transcription: bool = False,
    transcription_service: TranscriptionService = Depends(get_transcription_service)
) -> dict:
    """
    Endpoint to transcribe a YouTube video.

    Args:
        url (str): The URL of the YouTube video.
        return_only_vtt_transcription (bool): Whether to return only the VTT transcription.
        transcription_service (TranscriptionService): The transcription service dependency.

    Returns:
        dict: A dictionary containing the transcription.
    """
    try:
        logger.info(f"Received YouTube URL for transcription: {url}")
        transcription = transcription_service.transcribe_youtube_video(url, return_only_vtt_transcription)
        logger.info(f"Transcription completed for YouTube URL: {url}")
        return {"transcription": transcription}
    except Exception as e:
        logger.error(f"An error occurred during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")
