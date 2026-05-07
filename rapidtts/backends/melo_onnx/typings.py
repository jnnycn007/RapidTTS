# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from dataclasses import dataclass

import numpy as np


@dataclass
class MeloONNXInput:
    x: np.ndarray
    x_lengths: np.ndarray
    sid: np.ndarray
    tone: np.ndarray
    language: np.ndarray
    bert: np.ndarray
    ja_bert: np.ndarray
    noise_scale: np.ndarray
    length_scale: np.ndarray
    noise_scale_w: np.ndarray
    sdp_ratio: np.ndarray


@dataclass
class MeloONNXConfig:
    model_path: str
    device: str = "cpu"
