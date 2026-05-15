"""FastAPI application factory."""

from fastapi import FastAPI

from speech_io_hub.server.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="speech-io-hub",
        description="STT/TTS service for the Fante project",
        version="0.1.0",
    )
    app.include_router(health_router)
    return app
