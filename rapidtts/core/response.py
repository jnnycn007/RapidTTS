# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SynthesisResponse:
    audio: np.ndarray
    sample_rate: int
    audio_format: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def save(self, file_path: str):
        import soundfile

        soundfile.write(file_path, self.audio, samplerate=self.sample_rate)
