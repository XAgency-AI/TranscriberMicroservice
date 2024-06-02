from fastapi import FastAPI

from core.api.v1.handlers import router as transcription_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Transciber Microservice",
        docs_url="/api/docs",
        description="This microservice provides endpoints for transcribing audio and video files"
                    "using the Whisper API."
    )
    app.include_router(transcription_router)
    
    return app
