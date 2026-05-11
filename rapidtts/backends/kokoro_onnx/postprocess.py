# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import numpy as np

from ...core.response import SynthesisResponse
from .trim import trim as trim_audio


class KokoroONNXPostprocessor:
    def __init__(self):
        pass

    def run(self, audio_list, sample_rate, speed) -> SynthesisResponse:
        results = []
        for audio in audio_list:
            audio, _ = trim_audio(audio)
            results.append(audio)

        results = np.concatenate(results)
        return SynthesisResponse(
            audio=results, sample_rate=sample_rate, audio_format="wav"
        )
