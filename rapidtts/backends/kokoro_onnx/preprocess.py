# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from misaki.zh import ZHG2P

from ...common.io import load_json
from ...common.logger import logger
from ...common.text.normalization import create_text_normalizer
from ...core.request import SynthesisRequest
from ...core.typings import TextNormalizerType
from .tokenizer import Tokenizer
from .typings import KokoroONNXInput

EN_ZH_SEGMENT_PATTERN = re.compile(r"([A-Za-z \'-]*[A-Za-z][A-Za-z \'-]*)|([^A-Za-z]+)")


class KokoroONNXPreprocessor:
    def __init__(
        self,
        model_root_dir: Path,
        max_phoneme_length: int,
        voices: np.ndarray,
        text_normalizer_type: TextNormalizerType = TextNormalizerType.WETEXT,
    ) -> None:
        vocab_config = model_root_dir / "config.json"
        self.vocab = load_json(vocab_config)["vocab"]
        self.text_normalizer = create_text_normalizer(text_normalizer_type)

        self.zhg2p = ZHG2P(version="1.1")

        self.max_phoneme_length = max_phoneme_length

        self.tokenizer = Tokenizer(vocab=self.vocab)
        self.voices = voices

    def run(self, request: SynthesisRequest) -> list[KokoroONNXInput]:
        speed = request.extras.get("speed", 1.0)
        if speed < 0.5 or speed > 2.0:
            raise ValueError(f"Speed must be between 0.5 and 2.0, but got {speed}")

        voice = self.voices[request.extras.get("voice", "zm_009")]

        phonemes = self.g2p(request.text)
        batched_phoenemes = self.split_phonemes(phonemes)

        audios = []
        for phonemes in batched_phoenemes:
            audio_part = self.create_audio(phonemes, voice, speed)
            audios.append(audio_part)
        return audios

    def create_audio(
        self, phonemes: str, voice: np.ndarray, speed: float
    ) -> KokoroONNXInput:
        if len(phonemes) > self.max_phoneme_length:
            logger.warning(
                f"Phonemes are too long, truncating to {self.max_phoneme_length} phonemes"
            )
        phonemes = phonemes[: self.max_phoneme_length]

        tokens = np.array(self.tokenizer.tokenize(phonemes), dtype=np.int64)
        if len(tokens) > self.max_phoneme_length:
            raise ValueError(
                f"Tokenized phonemes exceed maximum length. Got {len(tokens)} tokens, but the maximum is {self.max_phoneme_length}."
            )

        voice = voice[len(tokens)]
        tokens = [[0, *tokens, 0]]
        return KokoroONNXInput(
            tokens=tokens,
            style=np.array(voice, dtype=np.float32),
            speed=np.array([speed], dtype=np.int32),
        )

    def g2p(self, text: str) -> str:
        text = self.text_normalizer.normalize(text)
        text = self.zhg2p.map_punctuation(text)
        if self.zhg2p.frontend is None:
            return self.zhg2p.legacy_call(text)

        en_callable = self.zhg2p.en_callable
        segments = []
        for en, zh in EN_ZH_SEGMENT_PATTERN.findall(text):
            en, zh = en.strip(), zh.strip()
            if zh:
                segments.append(self.zhg2p.frontend(zh)[0])
            elif en_callable is None:
                segments.append(self.tokenizer.phonemize(en))
            else:
                segments.append(en_callable(en))

        return " ".join(segments)

    def split_phonemes(self, phonemes: str) -> list[str]:
        """
        Split phonemes into batches of MAX_PHONEME_LENGTH
        Prefer splitting at punctuation marks.
        """
        words = re.split(r"([.,!?;])", phonemes)
        batched_phoenemes: list[str] = []
        current_batch = ""

        for part in words:
            part = part.strip()

            if part:
                if len(current_batch) + len(part) + 1 >= self.max_phoneme_length:
                    batched_phoenemes.append(current_batch.strip())
                    current_batch = part
                else:
                    if part in ".,!?;":
                        current_batch += part
                    else:
                        if current_batch:
                            current_batch += " "
                        current_batch += part

        if current_batch:
            batched_phoenemes.append(current_batch.strip())

        return batched_phoenemes
