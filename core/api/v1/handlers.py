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
        dict: A dictionary containing the transcription.

    Raises:
        HTTPException: If the file type is unsupported or an error occurs during transcription.
    """
    try:
        logger.info(f"Received file for transcription: {file.filename}")
        content = await file.read()
        mime_type, _ = mimetypes.guess_type(file.filename)

        if mime_type not in ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'video/mp4', 'audio/flac']:
            logger.error(f"Unsupported file type: {mime_type}")
            raise HTTPException(status_code=400, detail="Unsupported file type")

        transcription = transcription_service.transcribe_media_content(
            content=content, filename=file.filename,
        )

        logger.info(f"Transcription completed for file: {file.filename}")
        return {"transcription": transcription}
    except Exception as e:
        logger.error(f"An error occurred during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")
