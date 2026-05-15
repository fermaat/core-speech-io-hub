"""CLI: `python -m speech_io_hub` starts the HTTP service."""

import uvicorn

from speech_io_hub.config import SpeechSettings


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
