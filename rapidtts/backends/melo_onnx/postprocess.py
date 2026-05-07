# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import numpy as np

from ...core.response import SynthesisResponse


class MeloONNXPostprocessor:
    def __init__(self):
        pass

    def run(self, audio_list, sample_rate, speed) -> SynthesisResponse:
        audio = self._concat_audio(audio_list, sample_rate=sample_rate, speed=speed)
        return SynthesisResponse(
            audio=audio, sample_rate=sample_rate, audio_format="wav"
        )

    @staticmethod
    def _concat_audio(segment_data_list, sample_rate, speed=1.0):
        audio_segments = []
        for segment_data in segment_data_list:
            audio_segments += segment_data.reshape(-1).tolist()
            audio_segments += [0] * int((sample_rate * 0.05) / speed)
        audio_segments = np.array(audio_segments).astype(np.float32)
        return audio_segments
