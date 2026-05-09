# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import json
import sys
import types
from pathlib import Path

import pytest

from rapidtts.backends.melo_onnx import backend as melo_backend
from rapidtts.common.text import normalization
from rapidtts.common.text.normalization import (
    LegacyTextNormalizer,
    NoopTextNormalizer,
    TextNormalizer,
    WeTextNormalizer,
    create_text_normalizer,
)
from rapidtts.common.text.risk import detect_risky_tokens
from rapidtts.core.typings import TextNormalizerType


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_text_normalization_cases():
    fixture_path = FIXTURES_DIR / "text_normalization_cases.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_text_normalizer_base_interface_returns_none():
    assert TextNormalizer().normalize("测试") is None


@pytest.mark.parametrize(
    ("normalizer_type", "normalizer_cls"),
    [
        (TextNormalizerType.NONE, NoopTextNormalizer),
        (TextNormalizerType.LEGACY, LegacyTextNormalizer),
    ],
)
def test_create_text_normalizer_returns_expected_normalizer(
    normalizer_type, normalizer_cls
):
    assert isinstance(create_text_normalizer(normalizer_type), normalizer_cls)


def test_create_text_normalizer_rejects_unknown_normalizer_type():
    with pytest.raises(ValueError, match="Unsupported text normalizer"):
        create_text_normalizer("bad")


def test_noop_text_normalizer_returns_input_unchanged():
    text = "价格12.5元，电话13800138000"

    assert NoopTextNormalizer().normalize(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("价格12.5元", "价格十二点五元"),
        ("第2个版本", "第二个版本"),
        ("1个2.5元", "一个二点五元"),
        ("2026年", "二零二六年"),
        ("2026 年", "二零二六年"),
        ("今天是2026年5月8日", "今天是二零二六年五月八日"),
        ("今天是2026 年 5 月 8 日", "今天是二零二六年五月八日"),
        ("2026-05-08", "二零二六年五月八日"),
        ("￥13.5", "十三点五元"),
        ("6.3%", "百分之六点三"),
        ("增长6.3％", "增长百分之六点三"),
    ],
)
def test_legacy_text_normalizer_keeps_cn2an_number_behavior(text, expected):
    assert LegacyTextNormalizer().normalize(text) == expected


@pytest.mark.parametrize(
    "case", load_text_normalization_cases(), ids=lambda case: case["id"]
)
def test_legacy_text_normalizer_matches_golden_corpus(case):
    normalized = LegacyTextNormalizer().normalize(case["text"])

    assert normalized == case["legacy"]
    assert detect_risky_tokens(normalized) == []


def test_wetext_normalizer_delegates_to_wetext_normalizer(monkeypatch):
    seen = {}

    class FakeWetextNormalizer:
        def __init__(self, **kwargs):
            seen["kwargs"] = kwargs

        def normalize(self, text):
            seen["text"] = text
            return "归一化结果"

    fake_wetext = types.SimpleNamespace(Normalizer=FakeWetextNormalizer)
    monkeypatch.setitem(sys.modules, "wetext", fake_wetext)

    normalizer = WeTextNormalizer(lang="zh")

    assert normalizer.normalize("今天是2024年8月8日") == "归一化结果"
    assert seen == {
        "kwargs": {
            "lang": "zh",
            "operator": "tn",
            "remove_erhua": True,
        },
        "text": "今天是二零二四年8月8日",
    }


def test_wetext_normalizer_normalizes_four_digit_year_before_wetext(monkeypatch):
    class FakeWetextNormalizer:
        def __init__(self, **kwargs):
            pass

        def normalize(self, text):
            return text

    fake_wetext = types.SimpleNamespace(Normalizer=FakeWetextNormalizer)
    monkeypatch.setitem(sys.modules, "wetext", fake_wetext)

    normalizer = WeTextNormalizer(lang="zh")

    assert normalizer.normalize("今天是2026年5月8日") == "今天是二零二六年5月8日"
    assert normalizer.normalize("今天是2026 年5月8日") == "今天是二零二六年5月8日"


def test_wetext_normalizer_normalizes_license_plate_before_wetext(monkeypatch):
    class FakeWetextNormalizer:
        def __init__(self, **kwargs):
            pass

        def normalize(self, text):
            return text

    fake_wetext = types.SimpleNamespace(Normalizer=FakeWetextNormalizer)
    monkeypatch.setitem(sys.modules, "wetext", fake_wetext)

    normalizer = WeTextNormalizer(lang="zh")

    assert (
        normalizer.normalize("请播报车牌号码：京A86F29。")
        == "请播报车牌号码：京 A 八 六 F 二 九。"
    )
    assert normalizer.normalize("车牌粤B12345") == "车牌粤 B 一 二 三 四 五"


def test_wetext_normalizer_normalizes_uppercase_tokens_before_wetext(monkeypatch):
    class FakeWetextNormalizer:
        def __init__(self, **kwargs):
            pass

        def normalize(self, text):
            return text

    fake_wetext = types.SimpleNamespace(Normalizer=FakeWetextNormalizer)
    monkeypatch.setitem(sys.modules, "wetext", fake_wetext)

    normalizer = WeTextNormalizer(lang="zh")

    assert (
        normalizer.normalize("订单ID是AB20260508")
        == "订单I D 是A B 二 零 二 六 零 五 零 八"
    )
    assert (
        normalizer.normalize("请打开API文档，然后检查HTTP请求")
        == "请打开A P I 文档，然后检查H T T P 请求"
    )


def test_wetext_normalizer_reports_missing_optional_dependency(monkeypatch):
    monkeypatch.delitem(sys.modules, "wetext", raising=False)

    real_import = normalization.__builtins__["__import__"]

    def fake_import(name, *args, **kwargs):
        if name == "wetext":
            raise ImportError("No module named wetext")
        return real_import(name, *args, **kwargs)

    monkeypatch.setitem(normalization.__builtins__, "__import__", fake_import)

    with pytest.raises(ImportError, match="pip install wetext"):
        WeTextNormalizer()


def test_create_text_normalizer_builds_wetext_normalizer(monkeypatch):
    class FakeWetextNormalizer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def normalize(self, text):
            return text

    fake_wetext = types.SimpleNamespace(Normalizer=FakeWetextNormalizer)
    monkeypatch.setitem(sys.modules, "wetext", fake_wetext)

    normalizer = create_text_normalizer(TextNormalizerType.WETEXT, lang="zh")

    assert isinstance(normalizer, WeTextNormalizer)
    assert normalizer.normalizer.kwargs == {
        "lang": "zh",
        "operator": "tn",
        "remove_erhua": True,
    }


def test_melo_backend_converts_text_normalizer_config_to_enum(monkeypatch, tmp_path):
    seen = {}

    class FakeModel:
        def __init__(self, config):
            seen["model_path"] = config.model_path
            seen["device"] = config.device

    class FakePreprocessor:
        def __init__(self, model_root_dir, text_normalizer_type):
            seen["model_root_dir"] = model_root_dir
            seen["text_normalizer_type"] = text_normalizer_type

    monkeypatch.setattr(melo_backend, "MeloONNXModel", FakeModel)
    monkeypatch.setattr(melo_backend, "MeloONNXPreprocessor", FakePreprocessor)

    melo_backend.MeloONNXBackend(
        model_root_dir=tmp_path,
        device="cpu",
        text_normalizer_type="wetext",
    )

    assert seen["model_path"] == str(tmp_path / "tts_model.onnx")
    assert seen["device"] == "cpu"
    assert seen["model_root_dir"] == tmp_path
    assert seen["text_normalizer_type"] == TextNormalizerType.WETEXT


def test_melo_backend_defaults_to_wetext_normalizer(monkeypatch, tmp_path):
    seen = {}

    class FakeModel:
        def __init__(self, config):
            pass

    class FakePreprocessor:
        def __init__(self, model_root_dir, text_normalizer_type):
            seen["text_normalizer_type"] = text_normalizer_type

    monkeypatch.setattr(melo_backend, "MeloONNXModel", FakeModel)
    monkeypatch.setattr(melo_backend, "MeloONNXPreprocessor", FakePreprocessor)

    melo_backend.MeloONNXBackend(model_root_dir=tmp_path)

    assert seen["text_normalizer_type"] == TextNormalizerType.WETEXT


def test_melo_backend_rejects_invalid_text_normalizer_config(monkeypatch, tmp_path):
    class FakeModel:
        def __init__(self, config):
            pass

    monkeypatch.setattr(melo_backend, "MeloONNXModel", FakeModel)

    with pytest.raises(ValueError):
        melo_backend.MeloONNXBackend(
            model_root_dir=tmp_path,
            text_normalizer_type="bad",
        )
