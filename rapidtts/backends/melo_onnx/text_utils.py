# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from pathlib import Path

from ...core.typings import TextNormalizerType, TTSLanguage
from .kernel.symbols import language_id_map, language_tone_start_map, symbols


class TextUtils:
    def __init__(
        self,
        language: str,
        model_root_dir: Path,
        onnx_providers: list,
        session_opts=None,
        text_normalizer_type: TextNormalizerType = TextNormalizerType.LEGACY,
    ):
        self.language = language
        if self.language == TTSLanguage.ZH_MIX_EN.value:
            from .kernel.chinese_mix_en_kernel import ChineseMixEnKernel

            self.kernel = ChineseMixEnKernel(
                model_root_dir,
                onnx_providers,
                session_opts,
                text_normalizer_type=text_normalizer_type,
            )

        self.default_symbol_2_ID = {s: i for i, s in enumerate(symbols)}

    def clean_text(self, text):
        norm_text = self.kernel.text_normalize(text)
        phones, tones, word2ph = self.kernel.g2p(norm_text)
        return norm_text, phones, tones, word2ph

    def cleaned_text_to_sequence(self, cleaned_text, tones, language, symbol_to_id):
        symbol_to_id_map = symbol_to_id or self.default_symbol_2_ID
        phones = [symbol_to_id_map[symbol] for symbol in cleaned_text]

        tone_start = language_tone_start_map[language]
        tones = [i + tone_start for i in tones]

        lang_id = language_id_map[language]
        lang_ids = [lang_id for i in phones]
        return phones, tones, lang_ids
