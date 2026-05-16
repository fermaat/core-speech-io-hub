"""Piper-based TTS provider."""

import io
import wave
from pathlib import Path

from piper.voice import PiperVoice

from speech_io_hub.core.models import SynthesisResult
from speech_io_hub.registry import Entry, get


def synthesize_with_entry(text: str, entry: Entry) -> SynthesisResult:
    """Synthesize text using an already-resolved Piper registry entry."""
    piper_voice: PiperVoice = entry.instance
    sample_rate: int = piper_voice.config.sample_rate

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        piper_voice.synthesize_wav(text, wf)
    wav_bytes = buf.getvalue()

    with wave.open(io.BytesIO(wav_bytes), "rb") as wf2:
        duration = wf2.getnframes() / float(wf2.getframerate())

    return SynthesisResult(
        audio=wav_bytes,
        sample_rate=sample_rate,
        duration_seconds=duration,
        voice=entry.id,
    )


class PiperTTSProvider:
    """TTS provider delegating to a Piper voice held in the registry."""

    def synthesize(self, text: str, voice: str | None = None) -> SynthesisResult:
        entry = get(voice) if voice is not None else get(type="piper")
        return synthesize_with_entry(text, entry)


def load_piper_voice(onnx_path: str) -> PiperVoice:
    """Load a Piper voice from the path to its .onnx file.

    The companion .onnx.json config is discovered automatically if it sits next to the
    .onnx file (piper-tts default). Raises FileNotFoundError if the .onnx is missing.
    """
    onnx = Path(onnx_path)
    if not onnx.exists():
        raise FileNotFoundError(f"Piper voice not found: {onnx}")
    return PiperVoice.load(onnx_path)
