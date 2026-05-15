# speech-io-hub — Project Summary

## Purpose

Long-lived HTTP service that exposes STT (speech-to-text) and TTS (text-to-speech)
capabilities to downstream apps. Primary consumer is **Fante**, an RPG orchestrator for
a 2-year-old child. Target hardware: Apple Silicon M4.

---

## Architecture

```
src/speech_io_hub/
├── __init__.py
├── __main__.py              # Entry point: uvicorn via python -m speech_io_hub
├── cli.py                   # CLI: python -m speech_io_hub.cli record-and-transcribe
├── config.py                # SpeechSettings (pydantic-settings, env-file aware)
├── registry.py              # In-memory model registry (thread-safe); load/unload at runtime
├── audio/
│   ├── wav.py               # WAV bytes ↔ numpy float32 PCM conversion
│   ├── capture.py           # sounddevice mic capture (fixed duration)
│   └── vad.py               # silero-vad wrapper; record until speaker goes silent
├── core/
│   ├── base.py              # STTProvider / TTSProvider protocols
│   └── models.py            # TranscriptionResult, SynthesisResult (Pydantic)
├── providers/
│   ├── mock.py              # MockSTT, MockTTS — deterministic, no model required
│   └── whisper.py           # WhisperSTTProvider (faster-whisper) + load_whisper_model
├── server/
│   ├── app.py               # FastAPI factory; wires routers, bootstraps default model
│   └── routes/
│       ├── health.py        # GET /health
│       ├── transcribe.py    # POST /transcribe (multipart WAV upload)
│       └── models.py        # GET /models, POST /models/load, DELETE /models/{id}
└── client/
    └── client.py            # SpeechClient — httpx-based client for Fante
```

---

## Key classes / functions

| Name | File | Description |
|---|---|---|
| `SpeechSettings` | `config.py` | All config (host, port, provider, Whisper/VAD params). Reads from `.env` / env vars. |
| `STTProvider` | `core/base.py` | Protocol: `transcribe(audio, language, initial_prompt, model) -> TranscriptionResult` |
| `TranscriptionResult` | `core/models.py` | Pydantic model: `text`, `language`, `confidence`, `duration_seconds`, `model` |
| `ModelEntry` | `registry.py` | Dataclass holding a loaded model instance, its id, type, and source path |
| `register / get / unregister` | `registry.py` | Thread-safe registry CRUD; `get(None)` returns the default model |
| `WhisperSTTProvider` | `providers/whisper.py` | Fetches model from registry, calls faster-whisper, returns `TranscriptionResult` |
| `load_whisper_model` | `providers/whisper.py` | Instantiates a `WhisperModel`; `source` = canonical name or filesystem path |
| `wav_to_pcm / pcm_to_wav` | `audio/wav.py` | WAV ↔ mono float32 numpy array (handles multi-channel + 16/32-bit) |
| `record_until_silence` | `audio/vad.py` | Streams mic frames, runs silero-vad, stops on silence; returns WAV bytes |
| `SpeechClient` | `client/client.py` | httpx client: `.health()`, `.transcribe()`, `.list_models()`, `.load_model()`, `.unload_model()` |
| `create_app` | `server/app.py` | FastAPI factory; auto-loads default Whisper model if `speech_stt_provider=whisper` |

---

## Main entry points

```python
# Start server
# python -m speech_io_hub
# → uvicorn on speech_host:speech_port (default 127.0.0.1:8500)

# Downstream usage (from Fante or any Python app)
from speech_io_hub.client.client import SpeechClient

client = SpeechClient(base_url="http://127.0.0.1:8500")
result = client.transcribe(wav_bytes, language="es", initial_prompt="trepar, saltar")

# CLI smoke test
# python -m speech_io_hub.cli record-and-transcribe --prompt "trepar, saltar"
```

---

## HTTP API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/transcribe` | multipart: `audio` (WAV file), `language?`, `initial_prompt?`, `model?` |
| `GET` | `/models` | List loaded models |
| `POST` | `/models/load` | Load a Whisper model by canonical name or path |
| `DELETE` | `/models/{id}` | Unload a model from registry |

---

## Configuration (env vars / `.env`)

| Variable | Default | Description |
|---|---|---|
| `SPEECH_HOST` | `127.0.0.1` | Bind address |
| `SPEECH_PORT` | `8500` | Bind port |
| `SPEECH_STT_PROVIDER` | `mock` | `mock` or `whisper` |
| `SPEECH_WHISPER_DEFAULT_MODEL` | `base` | Canonical name or path loaded at startup |
| `SPEECH_WHISPER_DEVICE` | `auto` | `auto`, `cpu`, `cuda` |
| `SPEECH_WHISPER_COMPUTE_TYPE` | `auto` | `auto`, `float16`, `int8`, … |
| `SPEECH_WHISPER_DEFAULT_LANGUAGE` | `es` | Default language hint |
| `SPEECH_VAD_SILENCE_MS` | `800` | Silence gap to stop recording (ms) |
| `SPEECH_VAD_MAX_DURATION_S` | `30.0` | Hard cap on recording duration |
| `SPEECH_VAD_MIN_SPEECH_MS` | `250` | Minimum speech before silence triggers stop |

---

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | HTTP server framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data models and settings |
| `httpx` | HTTP client (SpeechClient) |
| `faster-whisper` | Whisper inference via CTranslate2 (Metal on Apple Silicon) |
| `sounddevice` | Microphone capture |
| `silero-vad` | Voice activity detection (ONNX-based) |
| `numpy` | PCM array manipulation |
| `python-multipart` | FastAPI multipart/form-data file uploads |
| `core-utils` | Shared CoreSettings base class |

Dev: `pytest`, `black`, `mypy`, `ruff`, `isort`, `pytest-cov`, `pytest-asyncio`

---

## Phase status

| Phase | Status | Description |
|---|---|---|
| 3.0 | ✅ Done | Protocols, MockSTT/TTS, FastAPI + `/health`, SpeechClient |
| 3.1 | ✅ Done | Whisper STT, VAD mic capture, model registry, HTTP model management |
| 3.2 | 🔜 Pending | TTS: Piper + system voice |
| 3.3+ | 🔜 Pending | Fine-tuned model loading, streaming transcription |

---

## Consumers / upstream

- **Fante** (downstream) — hits this service via `SpeechClient`
- **core-utils** (upstream) — provides `CoreSettings` base class
