# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from omegaconf import OmegaConf

cur_dir = Path(__file__).parent.resolve()
sys.path.append(str(cur_dir.parent))

from rapidtts import cli
from rapidtts.core import model_assets


@dataclass
class FakeSynthesisResponse:
    audio: np.ndarray
    sample_rate: int


def test_download_cli_passes_model_dir_and_progress_options(monkeypatch, tmp_path):
    seen = {}

    def fake_ensure_model_assets(model_name, local_dir=None, show_progress=True):
        seen["model_name"] = model_name
        seen["local_dir"] = local_dir
        seen["show_progress"] = show_progress
        return Path(local_dir)

    monkeypatch.setattr(cli, "ensure_model_assets", fake_ensure_model_assets)

    exit_code = cli.main(
        [
            "download",
            "melo_onnx",
            "--save-dir",
            str(tmp_path),
            "--no-progress",
            "--quiet",
        ]
    )

    assert exit_code == 0
    assert seen == {
        "model_name": "melo_onnx",
        "local_dir": str(tmp_path),
        "show_progress": False,
    }


def test_check_cli_success_without_backend_init(monkeypatch, capsys):
    backend_called = False

    monkeypatch.setattr(cli, "_check_package_import", lambda: True)
    monkeypatch.setattr(cli, "_check_dependencies", lambda: True)
    monkeypatch.setattr(cli, "_check_configs", lambda model_name: True)
    monkeypatch.setattr(cli, "_check_model_files", lambda model_name, model_dir: True)

    def fake_check_backend_init(model_name, model_dir):
        nonlocal backend_called
        backend_called = True
        return True

    monkeypatch.setattr(cli, "_check_backend_init", fake_check_backend_init)

    exit_code = cli.main(["check", "melo_onnx", "--quiet"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "RapidTTS installation looks ready." in captured.out
    assert backend_called is False


def test_check_cli_runs_backend_init_when_requested(monkeypatch):
    seen = {}

    monkeypatch.setattr(cli, "_check_package_import", lambda: True)
    monkeypatch.setattr(cli, "_check_dependencies", lambda: True)
    monkeypatch.setattr(cli, "_check_configs", lambda model_name: True)
    monkeypatch.setattr(cli, "_check_model_files", lambda model_name, model_dir: True)

    def fake_check_backend_init(model_name, model_dir):
        seen["model_name"] = model_name
        seen["model_dir"] = model_dir
        return True

    monkeypatch.setattr(cli, "_check_backend_init", fake_check_backend_init)

    exit_code = cli.main(
        [
            "check",
            "melo_onnx",
            "--model-dir",
            "custom_model_dir",
            "--init-backend",
            "--quiet",
        ]
    )

    assert exit_code == 0
    assert seen == {"model_name": "melo_onnx", "model_dir": "custom_model_dir"}


def test_check_cli_returns_failure_when_model_assets_fail(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_check_package_import", lambda: True)
    monkeypatch.setattr(cli, "_check_dependencies", lambda: True)
    monkeypatch.setattr(cli, "_check_configs", lambda model_name: True)
    monkeypatch.setattr(cli, "_check_model_files", lambda model_name, model_dir: False)

    exit_code = cli.main(["check", "melo_onnx", "--quiet"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "RapidTTS installation check failed." in captured.out


def test_text_cli_synthesizes_and_saves_audio(monkeypatch, tmp_path):
    seen = {}
    response = FakeSynthesisResponse(
        audio=np.array([0.1, 0.2], dtype=np.float32),
        sample_rate=16000,
    )

    def fake_run_tts(
        text,
        model_name,
        model_dir=None,
        language=None,
        speed=None,
        sample_rate=None,
        enable_log=True,
    ):
        seen["run_tts"] = {
            "text": text,
            "model_name": model_name,
            "model_dir": model_dir,
            "language": language,
            "speed": speed,
            "sample_rate": sample_rate,
            "enable_log": enable_log,
        }
        return response

    def fake_save_audio(output_path, audio, sample_rate):
        seen["save_audio"] = {
            "output_path": output_path,
            "audio": audio,
            "sample_rate": sample_rate,
        }
        return Path(output_path)

    monkeypatch.setattr(cli, "_run_tts", fake_run_tts)
    monkeypatch.setattr(cli, "_save_audio", fake_save_audio)

    output_path = tmp_path / "1.wav"
    exit_code = cli.main(
        [
            "text",
            "hello",
            str(output_path),
            "--model",
            "melo_onnx",
            "--model-dir",
            "custom_model_dir",
            "--language",
            "EN",
            "--speed",
            "1.2",
            "--sample-rate",
            "16000",
            "--quiet",
        ]
    )

    assert exit_code == 0
    assert seen["run_tts"] == {
        "text": "hello",
        "model_name": "melo_onnx",
        "model_dir": "custom_model_dir",
        "language": "EN",
        "speed": 1.2,
        "sample_rate": 16000,
        "enable_log": False,
    }
    assert seen["save_audio"]["output_path"] == str(output_path)
    assert seen["save_audio"]["audio"] is response.audio
    assert seen["save_audio"]["sample_rate"] == 16000


def test_check_model_assets_reports_missing_and_hash_mismatch(monkeypatch, tmp_path):
    good_file = tmp_path / "good.txt"
    bad_file = tmp_path / "bad.txt"
    good_file.write_text("ok", encoding="utf-8")
    bad_file.write_text("bad", encoding="utf-8")
    good_sha256 = hashlib.sha256(b"ok").hexdigest()

    cfg = OmegaConf.create(
        {
            "melo_onnx": {
                "base_url": "https://example.com/models",
                "local_dir": "unused",
                "files": [
                    {
                        "name": "good.txt",
                        "sha256": good_sha256,
                    },
                    {
                        "name": "bad.txt",
                        "sha256": (
                            "00000000000000000000000000000000"
                            "00000000000000000000000000000000"
                        ),
                    },
                    {
                        "name": "missing.txt",
                        "sha256": (
                            "11111111111111111111111111111111"
                            "11111111111111111111111111111111"
                        ),
                    },
                ],
            }
        }
    )
    monkeypatch.setattr(model_assets, "load_models_config", lambda: cfg)

    result = model_assets.check_model_assets("melo_onnx", local_dir=tmp_path)

    assert result.ok is False
    assert [item.name for item in result.missing_files] == ["missing.txt"]
    assert [item.name for item in result.hash_mismatch_files] == ["bad.txt"]


def test_check_model_assets_rejects_unknown_model(monkeypatch):
    monkeypatch.setattr(
        model_assets, "load_models_config", lambda: OmegaConf.create({})
    )

    with pytest.raises(ValueError, match="Unsupported model"):
        model_assets.check_model_assets("unknown")
