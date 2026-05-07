# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import pickle

from g2p_en import G2p

from .symbols import symbols
from .abstract_kernel import AbstractKernel

SYMBOL_SET = set(symbols)

ARPA_PHONEMES = {
    "AH0",
    "S",
    "AH1",
    "EY2",
    "AE2",
    "EH0",
    "OW2",
    "UH0",
    "NG",
    "B",
    "G",
    "AY0",
    "M",
    "AA0",
    "F",
    "AO0",
    "ER2",
    "UH1",
    "IY1",
    "AH2",
    "DH",
    "IY0",
    "EY1",
    "IH0",
    "K",
    "N",
    "W",
    "IY2",
    "T",
    "AA1",
    "ER1",
    "EH2",
    "OY0",
    "UH2",
    "UW1",
    "Z",
    "AW2",
    "AW1",
    "V",
    "UW2",
    "AA2",
    "ER",
    "AW0",
    "UW0",
    "R",
    "OW1",
    "EH1",
    "ZH",
    "AE0",
    "IH2",
    "IH",
    "Y",
    "JH",
    "P",
    "AY1",
    "EY0",
    "OY2",
    "TH",
    "HH",
    "D",
    "ER0",
    "CH",
    "AO1",
    "AE1",
    "AO2",
    "OY1",
    "AY2",
    "IH1",
    "OW0",
    "L",
    "SH",
}


class EnglishKernel(AbstractKernel):
    def __init__(self, g2p_dict_path):
        self.g2p_module = G2p()
        self.eng_dict = self.get_eng_dict(g2p_dict_path)

    @staticmethod
    def get_eng_dict(g2p_dict_path):
        with open(g2p_dict_path, "rb") as pickle_file:
            return pickle.load(pickle_file)

    def g2p_en(self, pad_start_end=True, tokenized=None):
        if tokenized is None:
            raise ValueError("tokenized must not be none")

        ph_groups = []
        for t in tokenized:
            if not t.startswith("#"):
                ph_groups.append([t])
            else:
                ph_groups[-1].append(t.replace("#", ""))

        phones, tones, word2ph = [], [], []
        for group in ph_groups:
            w = "".join(group)

            phone_len = 0
            word_len = len(group)
            if w.upper() in self.eng_dict:
                phns, tns = refine_syllables(self.eng_dict[w.upper()])
                phones += phns
                tones += tns
                phone_len += len(phns)
            else:
                phone_list = list(filter(lambda p: p != " ", self.g2p_module(w)))
                for ph in phone_list:
                    if ph in ARPA_PHONEMES:
                        ph, tn = refine_ph(ph)
                        phones.append(ph)
                        tones.append(tn)
                    else:
                        phones.append(ph)
                        tones.append(0)
                    phone_len += 1

            phone_distribution = distribute_phone(phone_len, word_len)
            word2ph += phone_distribution
        phones = [post_replace_ph(i) for i in phones]

        if pad_start_end:
            phones = ["_"] + phones + ["_"]
            tones = [0] + tones + [0]
            word2ph = [1] + word2ph + [1]
        return phones, tones, word2ph


def distribute_phone(n_phone, n_word):
    phones_per_word = [0] * n_word
    for task in range(n_phone):
        min_tasks = min(phones_per_word)
        min_index = phones_per_word.index(min_tasks)
        phones_per_word[min_index] += 1
    return phones_per_word


def refine_ph(phn):
    tone = 0
    if phn[-1:].isdigit():
        tone = int(phn[-1]) + 1
        phn = phn[:-1]
    return phn.lower(), tone


def refine_syllables(syllables):
    tones = []
    phonemes = []
    for phn_list in syllables:
        for i in range(len(phn_list)):
            phn = phn_list[i]
            phn, tone = refine_ph(phn)
            phonemes.append(phn)
            tones.append(tone)
    return phonemes, tones


def post_replace_ph(ph):
    rep_map = {
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
        "v": "V",
    }
    if ph in rep_map.keys():
        ph = rep_map[ph]

    return ph if ph in SYMBOL_SET else "UNK"
