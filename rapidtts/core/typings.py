# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from enum import Enum


class TTSModel(Enum):
    MELO_ONNX = "melo_onnx"


class TTSLanguage(Enum):
    ZH = "ZH"
    EN = "EN"
    ZH_MIX_EN = "ZH_MIX_EN"


class TextNormalizerType(Enum):
    LEGACY = "legacy"
    WETEXT = "wetext"
    NONE = "none"
