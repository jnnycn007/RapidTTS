# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from pathlib import Path
from typing import List

import numpy as np
import onnxruntime as ort

from ...common.device import normalize_execution_provider
from .typings import KokoroONNXConfig, KokoroONNXInput


class KokoroONNXModel:
    def __init__(self, config: KokoroONNXConfig) -> None:
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

    def speak(self, inputs: list[KokoroONNXInput]) -> List[np.ndarray]:
        results = []
        for input in inputs:
            audio = self.tts_infer.run(
                None,
                {
                    "input_ids": input.tokens,
                    "style": np.array(input.style, dtype=np.float32),
                    "speed": np.array(input.speed, dtype=np.int32),
                },
            )
            audio = audio[0]
            results.append(audio)
        return results

    @staticmethod
    def get_def_onnx_session_options():
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )
        return session_options
