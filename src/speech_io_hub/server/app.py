"""FastAPI application factory."""

from fastapi import FastAPI

from speech_io_hub.config import SpeechSettings
from speech_io_hub.providers.piper import load_piper_voice
from speech_io_hub.providers.system import SystemTTSProvider
from speech_io_hub.providers.whisper import load_whisper_model
from speech_io_hub.registry import Entry, default_id, register
from speech_io_hub.server.routes.health import router as health_router
from speech_io_hub.server.routes.models import router as models_router
from speech_io_hub.server.routes.synthesize import router as synthesize_router
from speech_io_hub.server.routes.transcribe import router as transcribe_router
from speech_io_hub.server.routes.voices import router as voices_router


def create_app() -> FastAPI:
    settings = SpeechSettings()
    app = FastAPI(
        title="speech-io-hub",
        description="STT/TTS service for the Fante project",
        version="0.3.0",
    )
    app.include_router(health_router)
    app.include_router(transcribe_router)
    app.include_router(models_router)
    app.include_router(synthesize_router)
    app.include_router(voices_router)

    if settings.speech_stt_provider == "whisper" and default_id("whisper") is None:
        instance = load_whisper_model(
            settings.speech_whisper_default_model,
            settings.speech_whisper_default_model,
            device=settings.speech_whisper_device,
            compute_type=settings.speech_whisper_compute_type,
        )
        register(
            Entry(
                id=settings.speech_whisper_default_model,
                type="whisper",
                instance=instance,
                source=settings.speech_whisper_default_model,
            ),
            as_default=True,
        )

    if settings.speech_tts_provider == "piper" and settings.speech_piper_default_voice_path:
        if default_id("piper") is None:
            instance_piper = load_piper_voice(settings.speech_piper_default_voice_path)
            register(
                Entry(
                    id="default-piper",
                    type="piper",
                    instance=instance_piper,
                    source=settings.speech_piper_default_voice_path,
                ),
                as_default=True,
            )
    elif settings.speech_tts_provider == "system" and default_id("system") is None:
        register(
            Entry(
                id="default-system",
                type="system",
                instance=SystemTTSProvider(),
                source=settings.speech_system_default_voice,
            ),
            as_default=True,
        )

    return app
