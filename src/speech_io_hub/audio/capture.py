"""Microphone capture via sounddevice."""

import numpy as np
import sounddevice as sd


def record_fixed(duration_s: float, sample_rate: int = 16000) -> np.ndarray:
    """Block for `duration_s` and return mono float32 PCM."""
    pcm = sd.rec(
        int(duration_s * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    return pcm.flatten()  # type: ignore[no-any-return]
