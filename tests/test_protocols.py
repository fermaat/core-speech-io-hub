"""Unit tests: MockSTT and MockTTS conform to STTProvider / TTSProvider protocols."""

import pytest

from speech_io_hub.core.base import STTProvider, TTSProvider
from speech_io_hub.core.models import SynthesisResult, TranscriptionResult
from speech_io_hub.providers.mock import MockSTT, MockTTS


@pytest.mark.unit
def test_mock_stt_satisfies_protocol() -> None:
    """MockSTT is structurally compatible with STTProvider."""
    stt: STTProvider = MockSTT()
    assert isinstance(stt, MockSTT)


@pytest.mark.unit
def test_mock_tts_satisfies_protocol() -> None:
    """MockTTS is structurally compatible with TTSProvider."""
    tts: TTSProvider = MockTTS()
    assert isinstance(tts, MockTTS)


@pytest.mark.unit
def test_mock_stt_returns_transcription_result() -> None:
    stt = MockSTT(response_text="prueba")
    audio = b"\x00" * 1024
    result = stt.transcribe(audio, language="es", initial_prompt="palabras clave")

    assert isinstance(result, TranscriptionResult)
    assert result.text == "prueba"
    assert result.language == "es"
    assert result.confidence == 1.0
    assert result.duration_seconds == 1.0
    assert result.model == "mock"


@pytest.mark.unit
def test_mock_stt_records_calls() -> None:
    stt = MockSTT()
    audio = b"\x00" * 512
    stt.transcribe(audio, language="en", model="my-model")

    assert len(stt.calls) == 1
    call = stt.calls[0]
    assert call["audio_size"] == 512
    assert call["language"] == "en"
    assert call["model"] == "my-model"


@pytest.mark.unit
def test_mock_tts_returns_synthesis_result() -> None:
    tts = MockTTS()
    result = tts.synthesize("hola mundo", voice="es-female")

    assert isinstance(result, SynthesisResult)
    assert result.audio == b"RIFF\x24\x00\x00\x00mock-wav"
    assert result.sample_rate == 22050
    assert result.voice == "es-female"
    assert result.duration_seconds > 0


@pytest.mark.unit
def test_mock_tts_default_voice() -> None:
    tts = MockTTS()
    result = tts.synthesize("texto de prueba")

    assert result.voice == "mock"


@pytest.mark.unit
def test_mock_tts_records_calls() -> None:
    tts = MockTTS()
    tts.synthesize("primera frase")
    tts.synthesize("segunda frase", voice="en-male")

    assert len(tts.calls) == 2
    assert tts.calls[0]["text"] == "primera frase"
    assert tts.calls[1]["voice"] == "en-male"
