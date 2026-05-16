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

    speech_stt_provider: str = "mock"
    speech_tts_provider: str = "mock"

    # Whisper
    speech_whisper_default_model: str = "base"
    speech_whisper_device: str = "auto"
    speech_whisper_compute_type: str = "auto"
    speech_whisper_default_language: str = "es"

    # VAD / capture
    speech_vad_silence_ms: int = 800
    speech_vad_max_duration_s: float = 30.0
    speech_vad_min_speech_ms: int = 250

    # TTS — Piper
    speech_piper_default_voice_path: str = ""  # empty → no Piper voice auto-loaded

    # TTS — System (macOS)
    speech_system_default_voice: str = "Mónica"  # any name from `say -v ?`


__all__ = ["SpeechSettings"]
