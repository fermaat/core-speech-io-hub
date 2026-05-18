# speech-io-hub

STT/TTS abstraction service for the [Fante](https://github.com/fermaat/fante-game-orchestrator)
project. Mirrors `core-llm-bridge`'s ports-and-adapters shape, but for voice I/O.

Runs as a long-lived HTTP process so models stay loaded in memory across sessions
and can be swapped at runtime.

## Install

```bash
pdm install --dev
```

## Run locally

```bash
pdm run python -m speech_io_hub       # starts service on 127.0.0.1:8500
curl http://127.0.0.1:8500/health     # → {"status": "ok"}
```

## Checks

```bash
./run_local_checks.sh
```

## VAD tuning for young children

The default voice-activity-detection thresholds were tuned for adult speech. Children
tend to pause longer mid-sentence, which causes the VAD to cut them off early. For a
2-year-old kid, the following overrides have worked well in practice:

```bash
SPEECH_VAD_SILENCE_MS=1500      # default 800
SPEECH_VAD_MAX_DURATION_S=45    # default 30
SPEECH_VAD_MIN_SPEECH_MS=400    # default 250
```

Set them in `.env` (or as environment variables) when running the service. No code
change required — see `SpeechSettings` in `config.py` for the full list.

## Phase

- Phase 3.0 — ✅ Done — protocols, mocks, FastAPI scaffold, client
- Phase 3.1 — ✅ Done — Whisper STT, VAD mic capture, model registry
- Phase 3.2 — ✅ Done — Piper + system TTS, `/synthesize`, `/voices*`
- Phase 3.3+ — pending: fine-tuned model loading, streaming transcription

See [SUMMARY.md](SUMMARY.md) for the full architecture and API reference.
