"""Shared domain types for speech I/O."""

from pydantic import BaseModel


class TranscriptionResult(BaseModel):
    """Result of an STT transcription."""

    text: str
    language: str | None = None
    confidence: float | None = None  # 0..1, provider-dependent
    duration_seconds: float | None = None  # input audio duration
    model: str | None = None  # which model id produced it


class SynthesisResult(BaseModel):
    """Result of a TTS synthesis."""

    audio: bytes  # WAV bytes
    sample_rate: int
    duration_seconds: float
    voice: str | None = None  # which voice id produced it
