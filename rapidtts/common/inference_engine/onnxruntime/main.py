# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from onnxruntime import GraphOptimizationLevel, InferenceSession, SessionOptions

from .provider_config import ProviderConfig


DEFAULT_SESSION_OPTIONS = {
    "log_severity_level": 4,
    "enable_cpu_mem_arena": True,
    "graph_optimization_level": GraphOptimizationLevel.ORT_ENABLE_ALL,
}


def build_session_options(cfg: Optional[Dict[str, Any]] = None) -> SessionOptions:
    options = SessionOptions()
    cfg = cfg or {}
    option_cfg = cfg.get("session_options", cfg) or {}
    option_values = dict(DEFAULT_SESSION_OPTIONS)
    option_values.update(option_cfg)

    for name, value in option_values.items():
        if value is None or not hasattr(options, name):
            continue

        option_attr = getattr(options, name)
        if callable(option_attr):
            continue

        if name in ("intra_op_num_threads", "inter_op_num_threads"):
            value = int(value)
            if value <= 0:
                continue

        if name == "graph_optimization_level" and isinstance(value, str):
            value = getattr(GraphOptimizationLevel, value)

        setattr(options, name, value)

    return options


class OrtInferSession:
    def __init__(self, model_path: Path, cfg: Dict[str, Any]):
        sess_opt = build_session_options(cfg.engine_cfg)
        provider_cfg = ProviderConfig(engine_cfg=cfg.engine_cfg)
        self.session = InferenceSession(
            str(model_path),
            sess_options=sess_opt,
            providers=provider_cfg.get_ep_list(),
        )
        provider_cfg.verify_providers(self.session.get_providers())

    def __call__(self, input_content: np.ndarray) -> np.ndarray:
        input_dict = dict(zip(self.get_input_names(), [input_content]))
        try:
            return self.session.run(self.get_output_names(), input_dict)
        except Exception as e:
            error_info = traceback.format_exc()
            raise ONNXRuntimeError(error_info) from e

    def get_input_names(self) -> List[str]:
        return [v.name for v in self.session.get_inputs()]

    def get_output_names(self) -> List[str]:
        return [v.name for v in self.session.get_outputs()]


class ONNXRuntimeError(Exception):
    pass
