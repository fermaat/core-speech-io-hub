"""Voice activity detection — record until the speaker stops talking."""

import numpy as np
import sounddevice as sd
from silero_vad import VADIterator, load_silero_vad

from speech_io_hub.audio.wav import pcm_to_wav

_VAD_SAMPLE_RATE = 16000
_FRAME_MS = 32
_FRAME_SAMPLES = _VAD_SAMPLE_RATE * _FRAME_MS // 1000


def record_until_silence(
    silence_ms: int = 800,
    max_duration_s: float = 30.0,
    min_speech_ms: int = 250,
) -> bytes:
    """Record from the default mic until the speaker has been silent for `silence_ms`.

    Stops after `max_duration_s` regardless (safety cap). Returns WAV bytes.
    Raises RuntimeError if no speech was ever detected.
    """
    model = load_silero_vad(onnx=True)
    vad = VADIterator(model, sampling_rate=_VAD_SAMPLE_RATE, min_silence_duration_ms=silence_ms)

    collected: list[np.ndarray] = []
    silence_acc_ms = 0
    speech_acc_ms = 0
    speech_started = False
    in_silence = False
    total_frames = 0
    max_frames = int(max_duration_s * 1000 / _FRAME_MS)

    with sd.InputStream(
        samplerate=_VAD_SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=_FRAME_SAMPLES,
    ) as stream:
        while total_frames < max_frames:
            frame, _ = stream.read(_FRAME_SAMPLES)
            frame_flat = frame.flatten()
            collected.append(frame_flat)
            total_frames += 1

            speech_dict = vad(frame_flat, return_seconds=False)
            if speech_dict and "start" in speech_dict:
                speech_started = True
                in_silence = False
                silence_acc_ms = 0
            if speech_dict and "end" in speech_dict:
                in_silence = True
                silence_acc_ms = 0
            if speech_started:
                if in_silence:
                    silence_acc_ms += _FRAME_MS
                else:
                    speech_acc_ms += _FRAME_MS
                if silence_acc_ms >= silence_ms and speech_acc_ms >= min_speech_ms:
                    break

    if not speech_started:
        raise RuntimeError("No speech detected.")

    pcm = np.concatenate(collected)
    return pcm_to_wav(pcm, _VAD_SAMPLE_RATE)
