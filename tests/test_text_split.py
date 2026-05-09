# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidtts.common.text.split import split_sentence


def test_split_sentence_keeps_decimal_numbers_together():
    text = "今天是2026-05-08，猪肉价格是￥13.5，增长6.3%"

    result = split_sentence(text, language="ZH_MIX_EN")

    assert "猪肉价格是￥13.5," in result
    assert "增长6.3%" in result[-1]
