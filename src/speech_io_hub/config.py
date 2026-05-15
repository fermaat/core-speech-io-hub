"""Speech I/O hub settings (subclass of core-utils CoreSettings)."""

from core_utils.settings import CoreSettings


class SpeechSettings(CoreSettings):
    model_config = {
        "env_file": [".env", ".env.local"],
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow",
    }

    speech_host: str = "127.0.0.1"
    speech_port: int = 8500

    # Provider selection (filled in for real providers in 3.1 and 3.2)
    speech_stt_provider: str = "mock"  # "mock" | "whisper" (in 3.1)
    speech_tts_provider: str = "mock"  # "mock" | "piper" | "system" (in 3.2)


__all__ = ["SpeechSettings"]
