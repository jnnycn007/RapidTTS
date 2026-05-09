# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Sequence

TextRuleFn = Callable[[str], str]

# ---------------------------------------------------------------------------
# Character maps
# ---------------------------------------------------------------------------

ZH_DIGITS = {
    "0": "零",
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
}

# Kept as a compatibility alias for normalization.py.
YEAR_DIGIT_MAP = ZH_DIGITS

EN_DIGITS = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}

EN_ONES = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
}

EN_TENS = {
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
}

LICENSE_PLATE_PROVINCES = (
    "京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领警学港澳"
)

CURRENCY_AMOUNT_CONTEXTS = ("金额是", "支付", "付款", "应付", "实付", "合计", "总计")
ORDER_NUMBER_CONTEXTS = ("订单号是", "订单编号是")
ROOM_NUMBER_CONTEXTS = ("房间号是", "房号是")
STATUS_CODE_CONTEXTS = ("状态码是否为", "状态码为")
MEASUREMENT_UNITS = ("GB", "MB", "KB", "TB")


# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------


def regex_union(values: Sequence[str]) -> str:
    return "|".join(re.escape(value) for value in values)


ALNUM_LEFT_BOUNDARY = r"(?<![A-Za-z0-9])"
ALNUM_RIGHT_BOUNDARY = r"(?![A-Za-z0-9])"
DIGIT_SEQUENCE_LEFT_BOUNDARY = r"(?<![\d.\-])"
DIGIT_SEQUENCE_RIGHT_BOUNDARY = r"(?!\.\d)(?![\d\-])"


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

LICENSE_PLATE_PATTERN = re.compile(
    rf"{ALNUM_LEFT_BOUNDARY}([{LICENSE_PLATE_PROVINCES}])\s*([A-Z])\s*"
    rf"([A-Z0-9]{{5,6}}){ALNUM_RIGHT_BOUNDARY}"
)
HYPHENATED_CODE_PATTERN = re.compile(
    rf"{ALNUM_LEFT_BOUNDARY}(?:[A-Z]{{2,}})(?:-[A-Z0-9]+)+{ALNUM_RIGHT_BOUNDARY}"
)
CURRENCY_AMOUNT_PATTERN = re.compile(
    rf"({regex_union(CURRENCY_AMOUNT_CONTEXTS)})\s*[￥¥]\s*(\d+\.\d{{1,2}})"
)
ORDER_NUMBER_PATTERN = re.compile(
    rf"({regex_union(ORDER_NUMBER_CONTEXTS)})\s*([A-Z]\d+){ALNUM_RIGHT_BOUNDARY}"
)
ROOM_NUMBER_PATTERN = re.compile(
    rf"({regex_union(ROOM_NUMBER_CONTEXTS)})\s*(\d{{2,5}})(?!\d)"
)
ENGLISH_PERCENTAGE_PATTERN = re.compile(r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)\s*%")
MEASUREMENT_UNIT_PATTERN = re.compile(
    rf"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)\s*"
    rf"({regex_union(MEASUREMENT_UNITS)}){ALNUM_RIGHT_BOUNDARY}"
)
ORDINAL_GE_PATTERN = re.compile(r"第\s*(\d+)\s*个")
STOCK_SYMBOL_PATTERN = re.compile(rf"{ALNUM_LEFT_BOUNDARY}([A-Z])\s*股")
UPPERCASE_TOKEN_PATTERN = re.compile(
    rf"{ALNUM_LEFT_BOUNDARY}(?:[A-Z]{{2,}}\d*|[A-Z]+\d+){ALNUM_RIGHT_BOUNDARY}"
)
STATUS_CODE_PATTERN = re.compile(
    rf"({regex_union(STATUS_CODE_CONTEXTS)})\s*(\d{{3}})(?!\d)"
)
ENGLISH_DIGIT_SEQUENCE_PATTERN = re.compile(
    r"(?<![\d.\-\u4e00-\u9fa5])\d{4,}(?!\.\d)(?![\d\-\u4e00-\u9fa5])"
)
DIGIT_SEQUENCE_PATTERN = re.compile(
    rf"{DIGIT_SEQUENCE_LEFT_BOUNDARY}\d{{4,}}{DIGIT_SEQUENCE_RIGHT_BOUNDARY}"
)
CHINESE_DATE_PATTERN = re.compile(
    r"(?<!\d)(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
)
CHINESE_YEAR_PATTERN = re.compile(r"(?<!\d)(\d{4})\s*年")
DUPLICATE_SPACE_PATTERN = re.compile(r"[ \t]{2,}")
SPACE_BEFORE_PUNCTUATION_PATTERN = re.compile(r"\s+([，。,.!?；：])")


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TextRule:
    name: str
    description: str
    apply: TextRuleFn


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def has_cjk(text: str) -> bool:
    return re.search(r"[\u4e00-\u9fff]", text) is not None


def has_ascii_letter(text: str) -> bool:
    return re.search(r"[A-Za-z]", text) is not None


def cleanup_spacing(text: str) -> str:
    text = DUPLICATE_SPACE_PATTERN.sub(" ", text)
    return SPACE_BEFORE_PUNCTUATION_PATTERN.sub(r"\1", text).strip()


def spell_zh_digits(token: str, separator: str = " ") -> str:
    return separator.join(ZH_DIGITS[char] for char in token)


def spell_en_digits(token: str, separator: str = " ") -> str:
    return separator.join(EN_DIGITS[char] for char in token)


def spell_digit_sequence(token: str, lang: str = "zh", separator: str = " ") -> str:
    if lang == "en":
        return spell_en_digits(token, separator=separator)
    return spell_zh_digits(token, separator=separator)


def spell_alnum_token(token: str) -> str:
    return " ".join(ZH_DIGITS[char] if char.isdigit() else char for char in token)


def spell_uppercase_letters(token: str) -> str:
    return " ".join(token)


def spell_license_plate_token(token: str) -> str:
    parts = []
    previous_is_letter = False
    for char in token:
        current_is_letter = "A" <= char <= "Z"
        current_is_digit = char.isdigit()
        word = ZH_DIGITS[char] if current_is_digit else char
        if current_is_letter and previous_is_letter:
            parts[-1] = f"{parts[-1]}、{word}"
        else:
            parts.append(word)
        previous_is_letter = current_is_letter
    return " ".join(parts)


def spell_english_int(value: int) -> str:
    if value < 20:
        return EN_ONES[value]
    if value < 100:
        ten_value = value // 10 * 10
        remainder = value % 10
        if remainder == 0:
            return EN_TENS[ten_value]
        return f"{EN_TENS[ten_value]} {EN_ONES[remainder]}"
    if value < 1000:
        remainder = value % 100
        prefix = f"{EN_ONES[value // 100]} hundred"
        if remainder == 0:
            return prefix
        return f"{prefix} {spell_english_int(remainder)}"
    return spell_digit_sequence(str(value), lang="en")


def spell_english_number(number: str) -> str:
    if "." not in number:
        return spell_english_int(int(number))

    integer, fraction = number.split(".", 1)
    return (
        f"{spell_english_int(int(integer))} point "
        f"{spell_digit_sequence(fraction, lang='en')}"
    )


@lru_cache(maxsize=1)
def cn2an_optional() -> Any | None:
    try:
        import cn2an
    except ImportError:
        return None
    return cn2an


def spell_rmb_decimal(amount: str, cn2an: Any) -> str:
    integer, fraction = amount.split(".", 1)
    result = f"{cn2an.an2cn(integer)}元"
    if not fraction or int(fraction) == 0:
        return result
    if len(fraction) == 1:
        return f"{result}{cn2an.an2cn(fraction)}角"

    jiao, fen = fraction[0], fraction[1]
    if jiao != "0":
        result += f"{cn2an.an2cn(jiao)}角"
    if fen != "0":
        if jiao == "0":
            result += "零"
        result += f"{cn2an.an2cn(fen)}分"
    return result


# ---------------------------------------------------------------------------
# Business rules
# ---------------------------------------------------------------------------


def normalize_license_plates(text: str) -> str:
    """Read Chinese vehicle plates as province + separated plate characters."""

    def convert_plate(match: re.Match) -> str:
        return spell_license_plate_token("".join(match.groups()))

    return LICENSE_PLATE_PATTERN.sub(convert_plate, text)


def normalize_hyphenated_codes(text: str) -> str:
    """Read identifiers like CN-2026-0008 character by character."""

    def convert_code(match: re.Match) -> str:
        return spell_alnum_token(match.group().replace("-", ""))

    return HYPHENATED_CODE_PATTERN.sub(convert_code, text)


def normalize_currency_amounts(text: str) -> str:
    """Read decimal RMB amounts in business payment contexts as yuan/jiao/fen."""

    cn2an = cn2an_optional()
    if cn2an is None:
        return text

    def convert_amount(match: re.Match) -> str:
        prefix, amount = match.groups()
        return f"{prefix}{spell_rmb_decimal(amount, cn2an)}"

    return CURRENCY_AMOUNT_PATTERN.sub(convert_amount, text)


def normalize_order_numbers(text: str) -> str:
    """Add a pause between a leading order letter and following digits."""

    def convert_order_number(match: re.Match) -> str:
        prefix, value = match.groups()
        return f"{prefix}{value[0]}、 {spell_digit_sequence(value[1:])}"

    return ORDER_NUMBER_PATTERN.sub(convert_order_number, text)


def normalize_room_numbers(text: str) -> str:
    """Read room numbers digit by digit instead of as cardinal values."""

    def convert_room_number(match: re.Match) -> str:
        prefix, value = match.groups()
        return f"{prefix}{spell_zh_digits(value, separator='')}"

    return ROOM_NUMBER_PATTERN.sub(convert_room_number, text)


def normalize_english_percentages(text: str) -> str:
    """Read percentages as 'percent' only in English-looking sentences."""

    if has_cjk(text) or not has_ascii_letter(text):
        return text

    return ENGLISH_PERCENTAGE_PATTERN.sub(
        lambda match: f"{spell_english_number(match.group(1))} percent",
        text,
    )


def normalize_measurement_units(text: str) -> str:
    """Read storage units like 12.3GB before wetext can misread them as dates."""

    cn2an = cn2an_optional()

    def convert_unit(match: re.Match) -> str:
        number, unit = match.groups()
        if has_cjk(text):
            number_text = cn2an.an2cn(number) if cn2an is not None else number
        else:
            number_text = spell_english_number(number)
        return f"{number_text} {spell_uppercase_letters(unit)}"

    return MEASUREMENT_UNIT_PATTERN.sub(convert_unit, text)


def normalize_ordinals(text: str) -> str:
    """Normalize '第2个' before wetext can produce the unnatural '第两个'."""

    cn2an = cn2an_optional()
    if cn2an is None:
        return text

    return ORDINAL_GE_PATTERN.sub(
        lambda match: f"第{cn2an.an2cn(match.group(1))}个",
        text,
    )


def normalize_stock_symbols(text: str) -> str:
    """Separate A股/B股 so the letter is read independently."""

    return STOCK_SYMBOL_PATTERN.sub(r"\1 股", text)


def normalize_uppercase_tokens(text: str) -> str:
    """Read uppercase abbreviations and alphanumeric IDs character by character."""

    text = UPPERCASE_TOKEN_PATTERN.sub(
        lambda match: spell_alnum_token(match.group()) + " ",
        text,
    )
    return cleanup_spacing(text)


def normalize_status_codes(text: str) -> str:
    """Read HTTP-like status codes in Chinese contexts digit by digit."""

    return STATUS_CODE_PATTERN.sub(
        lambda match: f"{match.group(1)}{spell_digit_sequence(match.group(2))}",
        text,
    )


def normalize_digit_sequences(text: str) -> str:
    """Read long standalone numbers as digit sequences, not numeric values."""

    text = ENGLISH_DIGIT_SEQUENCE_PATTERN.sub(
        lambda match: spell_digit_sequence(match.group(), lang="en"),
        text,
    )
    return DIGIT_SEQUENCE_PATTERN.sub(
        lambda match: spell_digit_sequence(match.group()),
        text,
    )


def normalize_year_digits(text: str) -> str:
    """Read calendar years digit by digit: 2026年 -> 二零二六年."""

    def convert_date(match: re.Match) -> str:
        year, month, day = match.groups()
        return f"{spell_zh_digits(year, separator='')}年{month}月{day}日"

    def convert_year(match: re.Match) -> str:
        return f"{spell_zh_digits(match.group(1), separator='')}年"

    text = CHINESE_DATE_PATTERN.sub(convert_date, text)
    return CHINESE_YEAR_PATTERN.sub(convert_year, text)


# Rules run from high-confidence structured tokens to broader fallbacks.
PRE_NORMALIZATION_RULES = (
    # Structured identifiers that must be protected before generic A-Z/number rules.
    TextRule(
        name="license_plate",
        description="Chinese vehicle plate numbers",
        apply=normalize_license_plates,
    ),
    TextRule(
        name="hyphenated_code",
        description="Hyphenated identifiers such as CN-2026-0008",
        apply=normalize_hyphenated_codes,
    ),

    # Contextual business numbers.
    TextRule(
        name="currency_amount",
        description="RMB decimal amounts in payment contexts",
        apply=normalize_currency_amounts,
    ),
    TextRule(
        name="order_number",
        description="Order numbers such as A10086",
        apply=normalize_order_numbers,
    ),
    TextRule(
        name="room_number",
        description="Room numbers such as 房间号是302",
        apply=normalize_room_numbers,
    ),

    # Language-sensitive numeric expressions.
    TextRule(
        name="english_percentage",
        description="English percentages such as 86.5%",
        apply=normalize_english_percentages,
    ),
    TextRule(
        name="measurement_unit",
        description="Storage units such as 12.3GB",
        apply=normalize_measurement_units,
    ),

    # Broad cleanup rules. Keep these after contextual rules.
    TextRule(
        name="ordinal",
        description="Chinese ordinal counters such as 第2个",
        apply=normalize_ordinals,
    ),
    TextRule(
        name="stock_symbol",
        description="Chinese stock symbols such as A股",
        apply=normalize_stock_symbols,
    ),
    TextRule(
        name="uppercase_token",
        description="Uppercase abbreviations and alphanumeric IDs",
        apply=normalize_uppercase_tokens,
    ),
    TextRule(
        name="status_code",
        description="Chinese HTTP status code contexts",
        apply=normalize_status_codes,
    ),
    TextRule(
        name="year_digits",
        description="Calendar years in Chinese date contexts",
        apply=normalize_year_digits,
    ),
    TextRule(
        name="digit_sequence",
        description="Long standalone digit sequences",
        apply=normalize_digit_sequences,
    ),
)


def apply_pre_normalization_rules(text: str) -> str:
    for rule in PRE_NORMALIZATION_RULES:
        text = rule.apply(text)
    return text
