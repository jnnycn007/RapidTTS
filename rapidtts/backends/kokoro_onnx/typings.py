# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from dataclasses import dataclass

import numpy as np


@dataclass
class KokoroONNXInput:
    tokens: list[list[int]]
    style: np.ndarray
    speed: np.ndarray


@dataclass
class KokoroONNXConfig:
    model_path: str
    device: str = "cpu"


@dataclass
class EspeakConfig:
    lib_path: str | None = None
    data_path: str | None = None
