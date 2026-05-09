# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import pytest

from rapidtts.common.text.risk import detect_risky_tokens


@pytest.mark.parametrize(
    ("text", "expected_rules"),
    [
        (
            "今天是2026-05-08，猪肉价格是￥13.5，增长6.3%",
            ["date_iso", "rmb_amount", "percentage"],
        ),
        ("请播报车牌号码：京A86F29。", ["license_plate"]),
        ("新能源车牌号码是浙AD12345。", ["license_plate"]),
        (
            "订单ID是AB20260508，金额是￥99.9。",
            ["contextual_order_number", "rmb_amount"],
        ),
        (
            "请打开API文档，然后检查HTTP请求状态码是否为200。",
            [
                "compact_uppercase_or_id",
                "compact_uppercase_or_id",
                "contextual_status_code",
            ],
        ),
        ("Please call me at 13800138000.", ["long_digit_sequence"]),
        ("The verification code is 123456.", ["long_digit_sequence"]),
        (
            "2026-05-08当天，A股成交额增长3.2%。",
            ["date_iso", "stock_symbol", "percentage"],
        ),
        (
            "CPU使用率为86.5%，内存占用为12.3GB。",
            ["compact_uppercase_or_id", "percentage", "storage_unit"],
        ),
        (
            "房间号是302，订单号是A10086。",
            ["contextual_room_number", "contextual_order_number"],
        ),
    ],
)
def test_detect_risky_tokens_reports_raw_high_risk_shapes(text, expected_rules):
    assert [risk.rule for risk in detect_risky_tokens(text)] == expected_rules


@pytest.mark.parametrize(
    "text",
    [
        "今天是二零二六年五月八日，猪肉价格是十三点五元，增长百分之六点三",
        "请播报车牌号码：京 A 八 六 F 二 九。",
        "订单I D 是A B 二 零 二 六 零 五 零 八，金额是九十九元九角。",
        "请打开A P I 文档，然后检查H T T P 请求状态码是否为二 零 零。",
        "The C P U usage is eighty six point five percent.",
        "房间号是三零二，订单号是A、 一 零 零 八 六。",
    ],
)
def test_detect_risky_tokens_ignores_normalized_text(text):
    assert detect_risky_tokens(text) == []
