"""macOS `say`-based TTS provider (always available; no model download needed)."""

import io
import os
import subprocess
import tempfile
import wave

from speech_io_hub.core.models import SynthesisResult
from speech_io_hub.registry import Entry, get, register


def synthesize_with_entry(text: str, entry: Entry) -> SynthesisResult:
    """Synthesize text using an already-resolved system voice registry entry."""
    macos_voice = entry.source

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    try:
        subprocess.run(
            [
                "say",
                "-v",
                macos_voice,
                "-o",
                wav_path,
                "--file-format=WAVE",
                "--data-format=LEI16@22050",
                text,
            ],
            check=True,
            capture_output=True,
        )
        with open(wav_path, "rb") as f:
            wav_bytes = f.read()
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)

    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        duration = wf.getnframes() / float(wf.getframerate())
        sample_rate = wf.getframerate()

    return SynthesisResult(
        audio=wav_bytes,
        sample_rate=sample_rate,
        duration_seconds=duration,
        voice=entry.id,
    )


class SystemTTSProvider:
    """TTS using the macOS `say` command. `source` on the entry is the macOS voice name
    (e.g. 'Mónica'), as listed by `say -v ?`."""

    def synthesize(self, text: str, voice: str | None = None) -> SynthesisResult:
        entry = get(voice) if voice is not None else get(type="system")
        return synthesize_with_entry(text, entry)


def register_system_voice(voice_id: str, macos_voice: str, as_default: bool = False) -> None:
    """Register a macOS `say` voice. No load step needed."""
    register(
        Entry(
            id=voice_id,
            type="system",
            instance=SystemTTSProvider(),
            source=macos_voice,
        ),
        as_default=as_default,
    )
