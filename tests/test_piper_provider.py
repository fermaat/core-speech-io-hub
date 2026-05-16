"""Functional test for the Piper TTS provider — skipped if voice file not downloaded."""

from pathlib import Path

import pytest

PIPER_VOICE = Path.home() / ".cache" / "speech-io-hub" / "piper" / "es_ES-davefx-medium.onnx"


@pytest.mark.functional
@pytest.mark.skipif(not PIPER_VOICE.exists(), reason="Piper voice not downloaded")
def test_piper_synthesizes(reset_registry: None) -> None:
    from speech_io_hub.providers.piper import PiperTTSProvider, load_piper_voice
    from speech_io_hub.registry import Entry, register

    voice = load_piper_voice(str(PIPER_VOICE))
    register(
        Entry(id="davefx", type="piper", instance=voice, source=str(PIPER_VOICE)),
        as_default=True,
    )
    result = PiperTTSProvider().synthesize("Hola mundo")
    assert result.audio[:4] == b"RIFF"
    assert result.duration_seconds > 0
    assert result.sample_rate > 0
