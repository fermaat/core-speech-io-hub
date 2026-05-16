"""POST /synthesize — text in, WAV bytes out."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from speech_io_hub.providers import piper as piper_mod
from speech_io_hub.providers import system as system_mod
from speech_io_hub.registry import Entry, get

router = APIRouter(tags=["tts"])


class SynthesizeRequest(BaseModel):
    text: str
    voice: str | None = None  # voice id; None → prefer piper default, then system


def _resolve_voice(voice_id: str | None) -> Entry:
    if voice_id is not None:
        try:
            return get(voice_id)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc
    for type_ in ("piper", "system"):
        try:
            return get(type=type_)
        except KeyError:
            continue
    raise HTTPException(404, "No TTS voice loaded")


@router.post("/synthesize")
def synthesize(body: SynthesizeRequest) -> Response:
    entry = _resolve_voice(body.voice)

    try:
        if entry.type == "piper":
            result = piper_mod.synthesize_with_entry(body.text, entry)
        elif entry.type == "system":
            result = system_mod.synthesize_with_entry(body.text, entry)
        else:
            raise HTTPException(500, f"Unknown voice type: {entry.type}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Synthesis failed: {exc}") from exc

    return Response(
        content=result.audio,
        media_type="audio/wav",
        headers={
            "X-Voice-Id": result.voice or "",
            "X-Sample-Rate": str(result.sample_rate),
            "X-Duration-Seconds": f"{result.duration_seconds:.3f}",
        },
    )
