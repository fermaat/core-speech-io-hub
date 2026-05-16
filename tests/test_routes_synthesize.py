"""Functional tests for POST /synthesize."""

import pytest
from fastapi.testclient import TestClient

from speech_io_hub.core.models import SynthesisResult
from speech_io_hub.registry import Entry, register


def _fake_wav() -> bytes:
    import io
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(b"\x00\x00" * 100)
    return buf.getvalue()


@pytest.mark.functional
def test_synthesize_returns_wav(
    test_client: TestClient, reset_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    wav = _fake_wav()
    fake_result = SynthesisResult(
        audio=wav, sample_rate=22050, duration_seconds=0.1, voice="monica"
    )
    monkeypatch.setattr(
        "speech_io_hub.server.routes.synthesize.system_mod.synthesize_with_entry",
        lambda text, entry: fake_result,
    )
    register(Entry(id="monica", type="system", instance=object(), source="Mónica"))

    response = test_client.post("/synthesize", json={"text": "Hola mundo"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content[:4] == b"RIFF"
    assert response.headers["x-voice-id"] == "monica"


@pytest.mark.functional
def test_synthesize_no_voice_loaded_returns_404(
    test_client: TestClient, reset_registry: None
) -> None:
    response = test_client.post("/synthesize", json={"text": "Hola"})
    assert response.status_code == 404


@pytest.mark.functional
def test_synthesize_prefers_piper_over_system(
    test_client: TestClient, reset_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    wav = _fake_wav()
    fake_result = SynthesisResult(
        audio=wav, sample_rate=22050, duration_seconds=0.1, voice="piper-voice"
    )
    monkeypatch.setattr(
        "speech_io_hub.server.routes.synthesize.piper_mod.synthesize_with_entry",
        lambda text, entry: fake_result,
    )
    register(Entry(id="piper-voice", type="piper", instance=object(), source="/v.onnx"))
    register(Entry(id="monica", type="system", instance=object(), source="Mónica"))

    response = test_client.post("/synthesize", json={"text": "Hola"})
    assert response.status_code == 200
    assert response.headers["x-voice-id"] == "piper-voice"


@pytest.mark.functional
def test_synthesize_specific_voice_by_id(
    test_client: TestClient, reset_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    wav = _fake_wav()
    fake_result = SynthesisResult(
        audio=wav, sample_rate=22050, duration_seconds=0.1, voice="monica"
    )
    monkeypatch.setattr(
        "speech_io_hub.server.routes.synthesize.system_mod.synthesize_with_entry",
        lambda text, entry: fake_result,
    )
    register(Entry(id="monica", type="system", instance=object(), source="Mónica"))

    response = test_client.post("/synthesize", json={"text": "Hola", "voice": "monica"})
    assert response.status_code == 200
