# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

from .rules import LICENSE_PLATE_PROVINCES


@dataclass(frozen=True)
class RiskyToken:
    rule: str
    token: str
    start: int
    end: int
    reason: str


@dataclass(frozen=True)
class RiskPattern:
    name: str
    reason: str
    pattern: re.Pattern[str]

    def finditer(self, text: str) -> Iterator[RiskyToken]:
        for match in self.pattern.finditer(text):
            yield RiskyToken(
                rule=self.name,
                token=match.group(),
                start=match.start(),
                end=match.end(),
                reason=self.reason,
            )


RISK_PATTERNS = (
    RiskPattern(
        name="license_plate",
        reason="Vehicle plates should separate province, letters, and digits",
        pattern=re.compile(
            rf"(?<![A-Za-z0-9])([{LICENSE_PLATE_PROVINCES}])\s*"
            rf"[A-Z]\s*[A-Z0-9]{{5,6}}(?![A-Za-z0-9])"
        ),
    ),
    RiskPattern(
        name="date_iso",
        reason="ISO-like dates should be normalized before TTS",
        pattern=re.compile(r"(?<!\d)\d{4}-\d{1,2}-\d{1,2}(?!\d)"),
    ),
    RiskPattern(
        name="rmb_amount",
        reason="RMB amounts should be normalized to yuan/jiao/fen or yuan",
        pattern=re.compile(r"[￥¥]\s*\d+(?:\.\d+)?"),
    ),
    RiskPattern(
        name="percentage",
        reason="Percentages should be normalized by language context",
        pattern=re.compile(r"(?<![A-Za-z0-9.])\d+(?:\.\d+)?\s*[%％]"),
    ),
    RiskPattern(
        name="storage_unit",
        reason="Storage units should separate the number and unit reading",
        pattern=re.compile(
            r"(?<![A-Za-z0-9.])\d+(?:\.\d+)?\s*(?:GB|MB|KB|TB)(?![A-Za-z0-9])"
        ),
    ),
    RiskPattern(
        name="contextual_room_number",
        reason="Room numbers should usually be read digit by digit",
        pattern=re.compile(r"(?:房间号|房号)是\s*\d{2,5}(?!\d)"),
    ),
    RiskPattern(
        name="contextual_order_number",
        reason="Order numbers should preserve letter/digit boundaries",
        pattern=re.compile(
            r"(?:订单号|订单编号|订单ID)是\s*[A-Z]*\d{4,}(?![A-Za-z0-9])"
        ),
    ),
    RiskPattern(
        name="contextual_status_code",
        reason="HTTP status codes should be read digit by digit",
        pattern=re.compile(r"(?:状态码是否为|状态码为)\s*\d{3}(?!\d)"),
    ),
    RiskPattern(
        name="stock_symbol",
        reason="Stock symbols such as A股 should separate the letter",
        pattern=re.compile(r"(?<![A-Za-z0-9])[A-Z]股"),
    ),
    RiskPattern(
        name="compact_uppercase_or_id",
        reason="Compact uppercase abbreviations or IDs may be misread by G2P",
        pattern=re.compile(
            r"(?<![A-Za-z0-9])(?:[A-Z]{2,}\d*|[A-Z]+\d+)(?![A-Za-z0-9])"
        ),
    ),
    RiskPattern(
        name="long_digit_sequence",
        reason="Long digit sequences are usually identifiers or phone-like numbers",
        pattern=re.compile(r"(?<![\d.\-])\d{4,}(?!\.\d)(?![\d\-])"),
    ),
)


def spans_overlap(first: tuple[int, int], second: tuple[int, int]) -> bool:
    return first[0] < second[1] and second[0] < first[1]


def detect_risky_tokens(text: str) -> list[RiskyToken]:
    """Return residual token shapes that are easy for TTS to misread."""

    risks = []
    seen_spans: list[tuple[int, int]] = []
    for risk_pattern in RISK_PATTERNS:
        for risk in risk_pattern.finditer(text):
            span = (risk.start, risk.end)
            if any(spans_overlap(span, seen_span) for seen_span in seen_spans):
                continue
            seen_spans.append(span)
            risks.append(risk)
    return sorted(risks, key=lambda risk: (risk.start, risk.end, risk.rule))
