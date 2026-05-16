"""Whisper-based STT provider built on faster-whisper."""

import logging
import time

import numpy as np
from faster_whisper import WhisperModel

from speech_io_hub.audio.wav import wav_to_pcm
from speech_io_hub.core.models import TranscriptionResult
from speech_io_hub.registry import get

logger = logging.getLogger(__name__)


class WhisperSTTProvider:
    """STT provider that delegates to a faster-whisper model from the registry."""

    def transcribe(
        self,
        audio: bytes,
        language: str | None = None,
        initial_prompt: str | None = None,
        model: str | None = None,
    ) -> TranscriptionResult:
        entry = get(model, type="whisper")
        wm: WhisperModel = entry.instance

        pcm, sr = wav_to_pcm(audio)
        if sr != 16000:
            pcm = _resample(pcm, sr, 16000)

        logger.info("Transcribing with model '%s' (%.2fs of audio)", entry.id, len(pcm) / 16000)
        t0 = time.monotonic()
        segments, info = wm.transcribe(
            pcm,
            language=language,
            initial_prompt=initial_prompt,
            beam_size=5,
            vad_filter=False,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        logger.info("Transcription done in %.2fs: %r", time.monotonic() - t0, text)

        return TranscriptionResult(
            text=text,
            language=info.language,
            confidence=getattr(info, "language_probability", None),
            duration_seconds=info.duration,
            model=entry.id,
        )


def _resample(pcm: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return pcm
    new_len = int(len(pcm) * sr_out / sr_in)
    xp = np.linspace(0, 1, num=len(pcm), endpoint=False)
    xn = np.linspace(0, 1, num=new_len, endpoint=False)
    return np.interp(xn, xp, pcm).astype("float32")  # type: ignore[no-any-return]


def load_whisper_model(
    model_id: str,
    source: str,
    device: str = "auto",
    compute_type: str = "auto",
) -> WhisperModel:
    """Instantiate a faster-whisper model. `source` is a canonical name ('base',
    'small'...) or a filesystem path to a converted model."""
    return WhisperModel(source, device=device, compute_type=compute_type)
