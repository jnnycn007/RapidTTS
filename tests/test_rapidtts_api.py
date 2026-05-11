# -*- encoding: utf-8 -*-
from rapidtts.core.tts import RapidTTS
from rapidtts.core.typings import ModelCapability, TTSModel


class FakeBackendWithVoices:
    def get_voices(self):
        return ["zf_001", "zm_009"]

    def get_capability(self):
        return ModelCapability(
            name="kokoro_onnx",
            languages=["ZH", "EN", "ZH_MIX_EN"],
            default_language="ZH_MIX_EN",
            voices=self.get_voices(),
            default_voice="zf_001",
            voice_source="voices-v1.1-zh.bin",
        )


class FakeBackendWithoutVoices:
    pass


def test_rapidtts_uses_global_backend_as_default_model(monkeypatch):
    seen = {}

    def fake_create_backend(self, model, **kwargs):
        seen["model"] = model
        seen["kwargs"] = kwargs
        return FakeBackendWithVoices()

    monkeypatch.setattr(RapidTTS, "create_backend", fake_create_backend)
    monkeypatch.setattr(
        "rapidtts.core.tts.ensure_model_assets",
        lambda backend_name: f"models/{backend_name}",
    )

    RapidTTS(enable_log=False)

    assert seen["model"] == TTSModel.KOKORO_ONNX
    assert seen["kwargs"]["model_root_dir"] == "models/kokoro_onnx"


def test_rapidtts_get_voices_delegates_to_backend():
    tts = RapidTTS.__new__(RapidTTS)
    tts.backend = FakeBackendWithVoices()

    assert tts.get_voices() == ["zf_001", "zm_009"]


def test_rapidtts_get_voices_returns_empty_list_for_backends_without_voices():
    tts = RapidTTS.__new__(RapidTTS)
    tts.backend = FakeBackendWithoutVoices()

    assert tts.get_voices() == []


def test_rapidtts_get_capability_delegates_to_backend():
    tts = RapidTTS.__new__(RapidTTS)
    tts.backend = FakeBackendWithVoices()

    capability = tts.get_capability()

    assert capability.name == "kokoro_onnx"
    assert capability.languages == ["ZH", "EN", "ZH_MIX_EN"]
    assert capability.voices == ["zf_001", "zm_009"]
