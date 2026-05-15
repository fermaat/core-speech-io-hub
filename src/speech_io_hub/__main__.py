"""CLI: `python -m speech_io_hub` starts the HTTP service."""

import logging

import uvicorn

from speech_io_hub.config import SpeechSettings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


def main() -> None:
    settings = SpeechSettings()
    uvicorn.run(
        "speech_io_hub.server.app:create_app",
        factory=True,
        host=settings.speech_host,
        port=settings.speech_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
