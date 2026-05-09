# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import pytest

from rapidtts.common.text.rules import (
    PRE_NORMALIZATION_RULES,
    apply_pre_normalization_rules,
    normalize_currency_amounts,
    normalize_digit_sequences,
    normalize_english_percentages,
    normalize_hyphenated_codes,
    normalize_license_plates,
    normalize_measurement_units,
    normalize_ordinals,
    normalize_order_numbers,
    normalize_room_numbers,
    normalize_status_codes,
    normalize_stock_symbols,
    normalize_uppercase_tokens,
    normalize_year_digits,
    spell_digit_sequence,
    spell_alnum_token,
)


def test_pre_normalization_rule_order_is_explicit():
    assert [rule.name for rule in PRE_NORMALIZATION_RULES] == [
        "license_plate",
        "hyphenated_code",
        "currency_amount",
        "order_number",
        "room_number",
        "english_percentage",
        "measurement_unit",
        "ordinal",
        "stock_symbol",
        "uppercase_token",
        "status_code",
        "year_digits",
        "digit_sequence",
    ]
    assert all(rule.description for rule in PRE_NORMALIZATION_RULES)


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("A", "A"),
        ("F29", "F 二 九"),
        ("AB20260508", "A B 二 零 二 六 零 五 零 八"),
        ("浙AD12345", "浙 A D 一 二 三 四 五"),
    ],
)
def test_spell_alnum_token_spells_digits_and_ascii_letters(token, expected):
    assert spell_alnum_token(token) == expected


def test_spell_digit_sequence_supports_chinese_and_english_digits():
    assert spell_digit_sequence("123456") == "一 二 三 四 五 六"
    assert spell_digit_sequence("302", separator="") == "三零二"
    assert spell_digit_sequence("123456", lang="en") == "one two three four five six"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("请播报车牌号码：京A86F29。", "请播报车牌号码：京 A 八 六 F 二 九。"),
        ("请播报车牌号码：粤B12345。", "请播报车牌号码：粤 B 一 二 三 四 五。"),
        ("车牌沪 D 12345", "车牌沪 D 一 二 三 四 五"),
        ("新能源车牌浙AD12345", "新能源车牌浙 A、D 一 二 三 四 五"),
    ],
)
def test_normalize_license_plates_handles_common_plate_shapes(text, expected):
    assert normalize_license_plates(text) == expected


def test_normalize_hyphenated_codes_spells_code_segments_digit_by_digit():
    assert normalize_hyphenated_codes("请播报编号：CN-2026-0008。") == (
        "请播报编号：C N 二 零 二 六 零 零 零 八。"
    )


def test_normalize_currency_amounts_reads_amount_decimal_as_jiao():
    assert normalize_currency_amounts("金额是￥99.9。") == "金额是九十九元九角。"


def test_normalize_order_numbers_adds_pause_after_leading_letter():
    assert normalize_order_numbers("房间号是302，订单号是A10086。") == (
        "房间号是302，订单号是A、 一 零 零 八 六。"
    )


def test_normalize_room_numbers_reads_room_ids_digit_by_digit():
    assert normalize_room_numbers("房间号是302，订单号是A10086。") == (
        "房间号是三零二，订单号是A10086。"
    )
    assert normalize_room_numbers("房号是1208。") == "房号是一二零八。"


def test_normalize_english_percentages_uses_percent_word():
    assert normalize_english_percentages("The CPU usage is 86.5%.") == (
        "The CPU usage is eighty six point five percent."
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("订单ID是AB20260508", "订单I D 是A B 二 零 二 六 零 五 零 八"),
        ("请打开API文档", "请打开A P I 文档"),
        ("检查HTTP请求", "检查H T T P 请求"),
    ],
)
def test_normalize_uppercase_tokens_spells_abbreviations_and_ids(text, expected):
    assert normalize_uppercase_tokens(text) == expected


def test_normalize_ordinals_prevents_wetext_from_reading_two_as_liang():
    assert normalize_ordinals("第2个版本将在下午4点发布。") == "第二个版本将在下午4点发布。"


def test_normalize_stock_symbols_separates_a_share_marker():
    assert normalize_stock_symbols("A股成交额增长3.2%。") == "A 股成交额增长3.2%。"


def test_normalize_measurement_units_separates_decimal_storage_units():
    assert normalize_measurement_units("内存占用为12.3GB。") == "内存占用为十二点三 G B。"
    assert normalize_measurement_units("memory usage is 12.3 GB.") == (
        "memory usage is twelve point three G B."
    )


def test_normalize_status_codes_reads_http_codes_digit_by_digit():
    assert normalize_status_codes("状态码是否为200。") == "状态码是否为二 零 零。"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Please call me at 13800138000.",
            "Please call me at one three eight zero zero one three eight zero zero zero.",
        ),
        (
            "The verification code is 123456.",
            "The verification code is one two three four five six.",
        ),
        ("验证码是123456。", "验证码是一 二 三 四 五 六。"),
    ],
)
def test_normalize_digit_sequences_reads_long_numbers_digit_by_digit(text, expected):
    assert normalize_digit_sequences(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026年", "二零二六年"),
        ("2026 年", "二零二六年"),
        ("今天是2026年5月8日", "今天是二零二六年5月8日"),
        ("今天是2026 年 5 月 8 日", "今天是二零二六年5月8日"),
    ],
)
def test_normalize_year_digits_spells_calendar_years_digit_by_digit(text, expected):
    assert normalize_year_digits(text) == expected


def test_apply_pre_normalization_rules_runs_rules_in_business_order():
    text = "新能源车牌浙AD12345，订单ID是AB20260508，日期是2026 年。"

    assert apply_pre_normalization_rules(text) == (
        "新能源车牌浙 A、D 一 二 三 四 五，"
        "订单I D 是A B 二 零 二 六 零 五 零 八，"
        "日期是二零二六年。"
    )
