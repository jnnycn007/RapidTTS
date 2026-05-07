# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import io
from typing import Optional

import numpy as np
import soundfile as sf


def encode_wav(audio: np.ndarray, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format="WAV")
    return buffer.getvalue()


def maybe_resample(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: Optional[int],
) -> tuple[np.ndarray, int]:
    if target_sr is None or target_sr == orig_sr:
        return audio, orig_sr

    import librosa

    out = librosa.resample(
        audio.astype("float32"),
        orig_sr=orig_sr,
        target_sr=target_sr,
    )
    return out.astype("float32"), target_sr
