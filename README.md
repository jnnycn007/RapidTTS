<div align="center">
  <h1><b>RapidTTS</b></h1>
  <b><font size="4"><i> 轻量级文本转语音工具，面向本地快速推理 </i></font></b>
  <div>&nbsp;</div>

<a href=""><img src="https://img.shields.io/badge/Python->=3.9,<4-aff.svg"></a>
<a href=""><img src="https://img.shields.io/badge/OS-Linux%2C%20Win%2C%20Mac-pink.svg"></a>
<a href="https://semver.org/"><img alt="SemVer2.0" src="https://img.shields.io/badge/SemVer-2.0-brightgreen"></a>
<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

</div>

## 简介

RapidTTS 是一个轻量级文本转语音工具，面向本地快速推理。当前默认后端是导出为 ONNX 的 MeloTTS。

## 特性

- 支持 MeloTTS ONNX 推理
- 支持中文、英文和中英混合文本
- 默认模型自动下载，并使用 SHA256 校验
- 提供命令行工具：下载模型、检查安装、文本合成
- 提供 Python API，便于集成到应用中

## 安装

```bash
git clone https://github.com/RapidAI/RapidTTS.git
cd RapidTTS
pip install -e .
```

## 快速使用

命令行合成：

```bash
rapidtts text "你好，RapidTTS" outputs/1.wav
```

Python 调用：

```python
from rapidtts import RapidTTS, SynthesisRequest, TTSModel

tts = RapidTTS(model=TTSModel.MELO_ONNX)
resp = tts.synthesize(SynthesisRequest(text="你好，RapidTTS"))
resp.save("outputs/1.wav")
```

## 文档

- [安装说明](docs/installation.md)
- [命令行用法](docs/cli.md)
- [Python API](docs/python_api.md)
- [模型文件](docs/models.md)
- [开发说明](docs/development.md)

## 致谢

- [MeloTTS](https://github.com/myshell-ai/MeloTTS)
- [melotts-onnx](https://pypi.org/project/melotts-onnx/)

## License

RapidTTS 使用 Apache-2.0 License。
