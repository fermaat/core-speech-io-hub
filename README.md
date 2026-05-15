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

## Phase

Currently **Phase 3.0** — scaffold only. No real STT/TTS engines yet.
- Phase 3.1 will add Whisper STT
- Phase 3.2 will add Piper/System TTS
