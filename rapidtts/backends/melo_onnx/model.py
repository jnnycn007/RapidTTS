# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from pathlib import Path

import numpy as np
import onnxruntime as ort

from ...common.device import normalize_execution_provider
from .typings import MeloONNXConfig, MeloONNXInput


class MeloONNXModel:
    def __init__(self, config: MeloONNXConfig) -> None:
        self.config = config

        if not Path(config.model_path).exists():
            raise FileNotFoundError(
                f'Can not found the onnx model file "{config.model_path}"'
            )

        exec_providers = [normalize_execution_provider(config.device)]
        onnx_session_options = self.get_def_onnx_session_options()
        self.tts_infer = ort.InferenceSession(
            config.model_path,
            sess_options=onnx_session_options,
            providers=exec_providers,
        )

    def speak(self, inputs: list[MeloONNXInput]):
        results = []
        for input in inputs:
            audio = self.tts_infer.run(
                None,
                {
                    "x": input.x,
                    "x_lengths": input.x_lengths,
                    "sid": input.sid,
                    "tone": input.tone,
                    "language": input.language,
                    "bert": input.bert.astype(np.float32),
                    "ja_bert": input.ja_bert.astype(np.float32),
                    "noise_scale": input.noise_scale.astype(np.float32),
                    "length_scale": input.length_scale.astype(np.float32),
                    "noise_scale_w": input.noise_scale_w.astype(np.float32),
                    "sdp_ratio": input.sdp_ratio.astype(np.float32),
                },
            )
            audio = audio[0][0, 0]
            results.append(audio)
        return results

    @staticmethod
    def get_def_onnx_session_options():
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )
        return session_options

    @staticmethod
    def _concat_audio(segment_data_list, sample_rate, speed=1.0):
        audio_segments = []
        for segment_data in segment_data_list:
            audio_segments += segment_data.reshape(-1).tolist()
            audio_segments += [0] * int((sample_rate * 0.05) / speed)
        audio_segments = np.array(audio_segments).astype(np.float32)
        return audio_segments


def tts_infer_factor(session):
    return lambda **kwargs: session.run(None, kwargs)[0][0, 0]
