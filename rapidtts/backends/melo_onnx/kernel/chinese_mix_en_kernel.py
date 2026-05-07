# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import re
from itertools import chain
from pathlib import Path
from typing import Union

import cn2an
import jieba.posseg as psg
from pypinyin import Style, lazy_pinyin
from tokenizers import Tokenizer

from .abstract_kernel import AbstractKernel
from .bert_infer import BertInfer
from .english_kernel import EnglishKernel
from .symbols import language_tone_start_map
from .tone_sandhi import ToneSandhi

PUNCTUATION = ["!", "?", "…", ",", ".", "'", "-"]

PUNCTUATION_REPLACEMENTS = {
    "：": ",",
    "；": ",",
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "·": ",",
    "、": ",",
    "...": "…",
    "$": ".",
    "“": "'",
    "”": "'",
    "‘": "'",
    "’": "'",
    "（": "'",
    "）": "'",
    "(": "'",
    ")": "'",
    "《": "'",
    "》": "'",
    "【": "'",
    "】": "'",
    "[": "'",
    "]": "'",
    "—": "-",
    "～": "-",
    "~": "-",
    "「": "'",
    "」": "'",
}

ENGLISH_SEGMENT_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z\s]*$")
ENGLISH_TEXT_PATTERN = re.compile(r"([a-zA-Z][a-zA-Z\s]*)")

FINAL_REPLACEMENTS = {
    "uei": "ui",
    "iou": "iu",
    "uen": "un",
}

PINYIN_REPLACEMENTS = {
    "ing": "ying",
    "i": "yi",
    "in": "yin",
    "u": "wu",
}

SINGLE_INITIAL_REPLACEMENTS = {
    "v": "yu",
    "e": "e",
    "i": "y",
    "u": "w",
}


class ChineseMixEnKernel(AbstractKernel):
    def __init__(self, model_root_dir: Path, onnx_providers: list, session_opts=None):
        tokenizer_path = model_root_dir / "tokenizer.json"
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))

        self.bert_infer = BertInfer(
            model_root_dir, onnx_providers, session_opts, self.tokenizer
        )

        g2p_dict_path = model_root_dir / "cmudict_cache.pickle"
        self.english_kernel = EnglishKernel(g2p_dict_path)

        self.tone_modifier = ToneSandhi()

        self.pinyin_to_symbol_map = self.load_pinyin_symbol_map(
            model_root_dir / "opencpop-strict.txt"
        )

        self.punctuation = PUNCTUATION
        self.rep_map = PUNCTUATION_REPLACEMENTS
        self.rep_pattern = re.compile("|".join(re.escape(p) for p in self.rep_map))

    def g2p(self, text):
        pattern = r"(?<=[{0}])\s*".format("".join(self.punctuation))
        sentences = [i for i in re.split(pattern, text) if i.strip() != ""]

        phones, tones, word2ph = self.g2p_mixed_segments(sentences)
        if sum(word2ph) != len(phones):
            raise ValueError(
                f"word2ph sum mismatch: sum(word2ph)={sum(word2ph)}, "
                f"phones={len(phones)}"
            )

        phones = ["_"] + phones + ["_"]
        tones = [0] + tones + [0]
        word2ph = [1] + word2ph + [1]
        return phones, tones, word2ph

    def g2p_mixed_segments(self, segments):
        splitter = "#$&^!@"
        phones_list, tones_list, word2ph = [], [], []

        for segment in segments:
            if splitter in segment:
                raise ValueError(
                    f"The splitter {splitter} is found in the text, please change another splitter."
                )

            segment = re.sub(
                ENGLISH_TEXT_PATTERN,
                lambda x: f"{splitter}{x.group(1)}{splitter}",
                segment,
            )
            pieces = segment.split(splitter)
            pieces = [piece for piece in pieces if len(piece) > 0]

            for piece in pieces:
                if ENGLISH_SEGMENT_PATTERN.fullmatch(piece):
                    # english
                    tokenized_en = self.tokenizer.encode(
                        piece, add_special_tokens=False
                    ).tokens

                    phones_en, tones_en, word2ph_en = self.english_kernel.g2p_en(
                        pad_start_end=False, tokenized=tokenized_en
                    )

                    # apply offset to tones_en
                    tones_en = [t + language_tone_start_map["EN"] for t in tones_en]
                    phones_list += phones_en
                    tones_list += tones_en
                    word2ph += word2ph_en
                    continue

                phones_zh, tones_zh, word2ph_zh = self.g2p_chinese_segments([piece])
                phones_list += phones_zh
                tones_list += tones_zh
                word2ph += word2ph_zh

        return phones_list, tones_list, word2ph

    def g2p_chinese_segments(self, segments):
        phones_list = []
        tones_list = []
        word2ph = []
        for seg in segments:
            seg = self.process_seg(seg)
            seg_cut = psg.lcut(seg)

            initials, finals = [], []
            seg_cut = self.tone_modifier.pre_merge_for_modify(seg_cut)
            for word, pos in seg_cut:
                sub_initials, sub_finals = self.get_initials_finals(word)
                sub_finals = self.tone_modifier.modified_tone(word, pos, sub_finals)
                initials.append(sub_initials)
                finals.append(sub_finals)

            initials = list(chain.from_iterable(initials))
            finals = list(chain.from_iterable(finals))
            for c, v in zip(initials, finals):
                phone, tone, w2p = self.process_cv(c, v, seg)
                word2ph += w2p
                phones_list += phone
                tones_list += tone

        return phones_list, tones_list, word2ph

    def process_seg(self, seg):
        return re.sub("[a-zA-Z]+", "", seg)

    def process_cv(self, c, v, seg):
        raw_pinyin = c + v
        if c == v:
            if c not in self.punctuation:
                raise ValueError(f"Unexpected punctuation phone: {c!r}, text={seg!r}")
            phone = [c]
            return phone, [0] * len(phone), [1]
        else:
            v_without_tone = v[:-1]
            tone = v[-1]

            pinyin = c + v_without_tone
            if tone not in "12345":
                raise ValueError(
                    f"Unexpected pinyin tone: {tone!r}, text={seg!r}, "
                    f"raw_pinyin={raw_pinyin!r}"
                )

            if c:
                # 多音节
                if v_without_tone in FINAL_REPLACEMENTS:
                    pinyin = c + FINAL_REPLACEMENTS[v_without_tone]
            else:
                # 单音节
                if pinyin in PINYIN_REPLACEMENTS:
                    pinyin = PINYIN_REPLACEMENTS[pinyin]
                else:
                    if pinyin[0] in SINGLE_INITIAL_REPLACEMENTS:
                        pinyin = SINGLE_INITIAL_REPLACEMENTS[pinyin[0]] + pinyin[1:]

            if pinyin not in self.pinyin_to_symbol_map:
                raise ValueError(
                    f"Unsupported pinyin: {pinyin!r}, text={seg!r}, "
                    f"raw_pinyin={raw_pinyin!r}"
                )
            phone = self.pinyin_to_symbol_map[pinyin].split(" ")
            len_phone = len(phone)

            return phone, [int(tone)] * len_phone, [len_phone]

    def text_normalize(self, text):
        numbers = re.findall(r"\d+(?:\.?\d+)?", text)
        for number in numbers:
            text = text.replace(number, cn2an.an2cn(number), 1)
        text = self.replace_punctuation(text)
        return text

    def replace_punctuation(self, text):
        text = text.replace("嗯", "恩").replace("呣", "母")

        replaced_text = self.rep_pattern.sub(lambda x: self.rep_map[x.group()], text)
        replaced_text = re.sub(
            r"[^\u4e00-\u9fa5_a-zA-Z\s" + "".join(self.punctuation) + r"]+",
            "",
            replaced_text,
        )
        replaced_text = re.sub(r"[\s]+", " ", replaced_text)
        return replaced_text

    def get_initials_finals(self, word):
        initials, finals = [], []
        orig_initials = lazy_pinyin(
            word, neutral_tone_with_five=True, style=Style.INITIALS
        )
        orig_finals = lazy_pinyin(
            word, neutral_tone_with_five=True, style=Style.FINALS_TONE3
        )
        for c, v in zip(orig_initials, orig_finals):
            initials.append(c)
            finals.append(v)
        return initials, finals

    @staticmethod
    def load_pinyin_symbol_map(file_path: Union[str, Path]):
        pinyin_to_symbol_map = {}
        with Path(file_path).open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid pinyin symbol map line {line_number}: {line!r}"
                    )
                pinyin_to_symbol_map[parts[0]] = parts[1]
        return pinyin_to_symbol_map
