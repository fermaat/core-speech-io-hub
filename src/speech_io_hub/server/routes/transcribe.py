"""POST /transcribe — accept a WAV upload, return text + metadata."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from speech_io_hub.providers.whisper import WhisperSTTProvider

router = APIRouter(tags=["stt"])

_provider = WhisperSTTProvider()


@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language: str | None = Form(default=None),
    initial_prompt: str | None = Form(default=None),
    model: str | None = Form(default=None),
) -> dict:  # type: ignore[type-arg]
    data = await audio.read()
    try:
        result = _provider.transcribe(
            data,
            language=language,
            initial_prompt=initial_prompt,
            model=model,
        )
    except KeyError as exc:
        raise HTTPException(
            503, f"No STT model loaded: {exc}. Start the server with SPEECH_STT_PROVIDER=whisper."
        ) from exc
    except Exception as exc:
        raise HTTPException(500, f"Transcription failed: {exc}") from exc
    return result.model_dump()
