# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from __future__ import annotations

import re

from ...common.logger import logger
from ...core.typings import TextNormalizerType


class TextNormalizer:
    def normalize(self, text: str) -> str:
        pass


class NoopTextNormalizer(TextNormalizer):
    def normalize(self, text: str) -> str:
        return text


class LegacyTextNormalizer(TextNormalizer):
    def normalize(self, text: str) -> str:
        import cn2an

        numbers = re.findall(r"\d+(?:\.?\d+)?", text)
        for number in numbers:
            text = text.replace(number, cn2an.an2cn(number), 1)
        return text


class WeTextNormalizer(TextNormalizer):
    def __init__(self, lang: str = "auto") -> None:
        try:
            from wetext import Normalizer
        except ImportError:
            raise ImportError(
                "WeText is not installed. Please install it with `pip install wetext`."
            )

        self.normalizer = Normalizer(lang=lang, operator="tn", remove_erhua=True)

    def normalize(self, text: str) -> str:
        return self.normalizer.normalize(text)


def create_text_normalizer(
    normalizer_type: TextNormalizerType, **kwargs
) -> TextNormalizer:
    if normalizer_type == TextNormalizerType.NONE:
        return NoopTextNormalizer()

    if normalizer_type == TextNormalizerType.LEGACY:
        logger.info("Using LegacyTextNormalizer for text normalization.")
        return LegacyTextNormalizer()

    if normalizer_type == TextNormalizerType.WETEXT:
        logger.info("Using WeTextNormalizer for text normalization.")
        return WeTextNormalizer(**kwargs)

    raise ValueError(
        f"Unsupported text normalizer: {normalizer_type}. "
        f"Expected one of: {', '.join([v.value for v in TextNormalizerType])}."
    )
