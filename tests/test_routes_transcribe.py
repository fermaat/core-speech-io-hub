"""Functional tests for POST /transcribe."""

import io
import wave

import pytest
from fastapi.testclient import TestClient

from speech_io_hub.core.models import TranscriptionResult


def _make_wav(duration_s: float = 0.1, sample_rate: int = 16000) -> bytes:
    """Generate a minimal silent WAV blob for testing."""
    import numpy as np

    n_samples = int(duration_s * sample_rate)
    silence = (np.zeros(n_samples, dtype=np.int16)).tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(silence)
    return buf.getvalue()


@pytest.mark.functional
def test_transcribe_returns_text(
    test_client: TestClient, reset_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_result = TranscriptionResult(
        text="hola mundo",
        language="es",
        confidence=0.99,
        duration_seconds=0.1,
        model="base",
    )
    monkeypatch.setattr(
        "speech_io_hub.server.routes.transcribe._provider.transcribe",
        lambda *args, **kwargs: fake_result,
    )

    wav = _make_wav()
    response = test_client.post(
        "/transcribe",
        files={"audio": ("test.wav", wav, "audio/wav")},
        data={"language": "es"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "hola mundo"
    assert body["language"] == "es"


@pytest.mark.functional
def test_transcribe_no_model_loaded_returns_404(
    test_client: TestClient, reset_registry: None
) -> None:
    wav = _make_wav()
    response = test_client.post(
        "/transcribe",
        files={"audio": ("test.wav", wav, "audio/wav")},
    )
    assert response.status_code == 404
