# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from dataclasses import dataclass, field
from typing import Any, Optional

from .typings import TTSLanguage


@dataclass
class SynthesisRequest:
    text: str
    language: Optional[TTSLanguage] = None
    voice: Optional[str] = None
    speed: Optional[float] = None
    sample_rate: Optional[int] = None
    audio_format: Optional[str] = None
    extras: dict[str, Any] = field(default_factory=dict)
