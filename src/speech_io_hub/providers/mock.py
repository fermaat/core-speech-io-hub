"""Mock providers — return canned data, no real models."""

from speech_io_hub.core.models import SynthesisResult, TranscriptionResult


class MockSTT:
    def __init__(self, response_text: str = "hola mundo") -> None:
        self._response = response_text
        self.calls: list[dict[str, object]] = []

    def transcribe(
        self,
        audio: bytes,
        language: str | None = None,
        initial_prompt: str | None = None,
        model: str | None = None,
    ) -> TranscriptionResult:
        self.calls.append(
            {
                "audio_size": len(audio),
                "language": language,
                "initial_prompt": initial_prompt,
                "model": model,
            }
        )
        return TranscriptionResult(
            text=self._response,
            language=language or "es",
            confidence=1.0,
            duration_seconds=1.0,
            model=model or "mock",
        )


class MockTTS:
    def __init__(self, audio_bytes: bytes = b"RIFF\x24\x00\x00\x00mock-wav") -> None:
        self._audio = audio_bytes
        self.calls: list[dict[str, object]] = []

    def synthesize(
        self,
        text: str,
        voice: str | None = None,
    ) -> SynthesisResult:
        self.calls.append({"text": text, "voice": voice})
        return SynthesisResult(
            audio=self._audio,
            sample_rate=22050,
            duration_seconds=float(len(text)) * 0.05,
            voice=voice or "mock",
        )
