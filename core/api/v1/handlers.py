import mimetypes

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from core.services.transcriber import TranscriptionService
from core.dependencies import get_transcription_service


router = APIRouter(tags=['Transcriptions'])

@router.post("/transcribe/")
async def create_transcription(
    file: UploadFile = File(...),
    transcription_service: TranscriptionService = Depends(get_transcription_service)
) -> dict:
    try:
        content = await file.read()
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type not in ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'video/mp4', 'audio/flac']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        transcription = transcription_service.transcribe_media_content(
            content=content, filename=file.filename,
        )
        
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")