"""WAV bytes <-> numpy PCM conversion helpers."""

import io
import wave

import numpy as np


def wav_to_pcm(data: bytes) -> tuple[np.ndarray, int]:
    """Decode WAV bytes into mono float32 PCM at the file's native sample rate."""
    with wave.open(io.BytesIO(data), "rb") as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())

    if sampwidth == 2:
        pcm = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        pcm = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported WAV sampwidth: {sampwidth}")

    if n_channels > 1:
        pcm = pcm.reshape(-1, n_channels).mean(axis=1)
    return pcm, sr


def pcm_to_wav(pcm: np.ndarray, sample_rate: int) -> bytes:
    """Encode mono float32 PCM (-1..1) into 16-bit WAV bytes."""
    clipped = np.clip(pcm, -1.0, 1.0)
    int16 = (clipped * 32767.0).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16.tobytes())
    return buf.getvalue()
