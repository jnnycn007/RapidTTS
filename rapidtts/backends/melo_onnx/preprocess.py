# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from __future__ import annotations

import re
from pathlib import Path
from typing import List

import numpy as np

from ...common.io import load_json
from ...common.text.split import split_sentence
from ...core.request import SynthesisRequest
from ...core.typings import TextNormalizerType
from .text_utils import TextUtils
from .typings import MeloONNXInput


class MeloONNXPreprocessor:
    def __init__(
        self,
        model_root_dir: Path,
        text_normalizer_type: TextNormalizerType = TextNormalizerType.LEGACY,
    ) -> None:
        config_path = model_root_dir / "configuration.json"
        self.params = load_json(config_path)
        self.symbol_to_id = {s: i for i, s in enumerate(self.params["symbols"])}

        exec_providers = ["CPUExecutionProvider"]
        onnx_session_options = None
        self.text_utils = TextUtils(
            "ZH_MIX_EN",
            model_root_dir,
            exec_providers,
            onnx_session_options,
            text_normalizer_type,
        )

    def run(self, request: SynthesisRequest) -> List[MeloONNXInput]:
        language = request.language.value
        self.language = language

        speaker_id = self.params["data"]["spk2id"][language]

        results = []
        texts = split_sentence(request.text, language=language)
        for sentence in texts:
            if language in ["EN", "ZH_MIX_EN"]:
                sentence = re.sub(r"([a-z])([A-Z])", r"\1 \2", sentence)

            bert, ja_bert, phones, tones, lang_ids = self._get_text_for_tts_infer(
                sentence
            )

            x_tst = np.expand_dims(phones, axis=0)
            tones = np.expand_dims(tones, axis=0)
            lang_ids = np.expand_dims(lang_ids, axis=0)
            bert = np.expand_dims(bert, axis=0)
            ja_bert = np.expand_dims(ja_bert, axis=0)
            x_tst_lengths = np.array([phones.shape[0]], dtype=np.int64)
            del phones
            speakers = np.array([speaker_id], dtype=np.int64)

            results.append(
                MeloONNXInput(
                    x=x_tst,
                    x_lengths=x_tst_lengths,
                    sid=speakers,
                    tone=tones,
                    language=lang_ids,
                    bert=bert.astype(np.float32),
                    ja_bert=ja_bert.astype(np.float32),
                    noise_scale=np.array(
                        request.extras["noise_scale"], dtype=np.float32
                    ),
                    length_scale=np.array(1.0 / request.speed, dtype=np.float32),
                    noise_scale_w=np.array(
                        request.extras["noise_scale_w"], dtype=np.float32
                    ),
                    sdp_ratio=np.array(request.extras["sdp_ratio"], dtype=np.float32),
                )
            )
        return results

    def _get_text_for_tts_infer(self, text):
        norm_text, phone, tone, word2ph = self.text_utils.clean_text(text)
        phone, tone, language = self.text_utils.cleaned_text_to_sequence(
            phone, tone, self.language, self.symbol_to_id
        )
        if self.params["data"]["add_blank"]:
            phone = intersperse(phone, 0)
            tone = intersperse(tone, 0)
            language = intersperse(language, 0)
            for i in range(len(word2ph)):
                word2ph[i] = word2ph[i] * 2
            word2ph[0] += 1

        if self.params["data"].get("disable_bert", False):
            bert = np.zeros((1024, len(phone)))
            ja_bert = np.zeros((768, len(phone)))
        else:
            bert = self.text_utils.kernel.bert_infer.get_bert_feature(
                norm_text, word2ph
            )
            del word2ph
            assert bert.shape[-1] == len(phone), phone

            if self.language == "ZH":
                ja_bert = np.zeros((768, len(phone)))
            elif self.language in [
                "JP",
                "EN",
                "ZH_MIX_EN",
                "KR",
                "SP",
                "ES",
                "FR",
                "DE",
                "RU",
            ]:
                ja_bert = bert
                bert = np.zeros((1024, len(phone)))
            else:
                raise NotImplementedError()

        assert bert.shape[-1] == len(phone), (
            f"Bert seq len {bert.shape[-1]} != {len(phone)}"
        )

        phone = np.array(phone, dtype=np.int64)
        tone = np.array(tone, dtype=np.int64)
        language = np.array(language, dtype=np.int64)
        return bert, ja_bert, phone, tone, language


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 + 1)
    result[1::2] = lst
    return result
