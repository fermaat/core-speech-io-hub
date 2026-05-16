"""Play WAV bytes through the default audio output."""

import sounddevice as sd

from speech_io_hub.audio.wav import wav_to_pcm


def play_wav(wav_bytes: bytes, blocking: bool = True) -> None:
    pcm, sr = wav_to_pcm(wav_bytes)
    sd.play(pcm, sr)
    if blocking:
        sd.wait()
