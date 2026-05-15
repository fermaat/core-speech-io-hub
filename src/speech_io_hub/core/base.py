"""Provider protocols for STT and TTS."""

from typing import Protocol

from speech_io_hub.core.models import SynthesisResult, TranscriptionResult


class STTProvider(Protocol):
    def transcribe(
        self,
        audio: bytes,
        language: str | None = None,
        initial_prompt: str | None = None,
        model: str | None = None,
    ) -> TranscriptionResult:
        """Transcribe a WAV-encoded audio blob.

        `initial_prompt` biases the recognizer toward a vocabulary (useful for
        kid speech and domain-specific words). `model` selects among loaded
        models when the provider supports hot-swap; None means default.
        """
        ...


class TTSProvider(Protocol):
    def synthesize(
        self,
        text: str,
        voice: str | None = None,
    ) -> SynthesisResult:
        """Synthesize text to WAV audio."""
        ...
