"""FastAPI application factory."""

from fastapi import FastAPI

from speech_io_hub.config import SpeechSettings
from speech_io_hub.providers.whisper import load_whisper_model
from speech_io_hub.registry import ModelEntry, default_id, register
from speech_io_hub.server.routes.health import router as health_router
from speech_io_hub.server.routes.models import router as models_router
from speech_io_hub.server.routes.transcribe import router as transcribe_router


def create_app() -> FastAPI:
    settings = SpeechSettings()
    app = FastAPI(
        title="speech-io-hub",
        description="STT/TTS service for the Fante project",
        version="0.2.0",
    )
    app.include_router(health_router)
    app.include_router(transcribe_router)
    app.include_router(models_router)

    if settings.speech_stt_provider == "whisper" and default_id() is None:
        instance = load_whisper_model(
            settings.speech_whisper_default_model,
            settings.speech_whisper_default_model,
            device=settings.speech_whisper_device,
            compute_type=settings.speech_whisper_compute_type,
        )
        register(
            ModelEntry(
                id=settings.speech_whisper_default_model,
                type="whisper",
                instance=instance,
                source=settings.speech_whisper_default_model,
            ),
            as_default=True,
        )
    return app
