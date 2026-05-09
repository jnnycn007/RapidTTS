<div align="center">
  <img src="https://github.com/RapidAI/RapidTTS/releases/download/v1.0.1/logo.jpg" width="80%">

  <h1><b>🎙 RapidTTS</b></h1>
  <b><font size="4"><i> 轻量级文本转语音工具，面向本地快速推理 </i></font></b>
  <div>&nbsp;</div>

<!-- <a href="https://huggingface.co/spaces/RapidAI/RapidTTS" target="_blank"><img src="https://img.shields.io/badge/Hugging Face-Demo-blue?style=flat-square"></a> -->
<a href="https://www.modelscope.cn/studios/RapidAI/RapidTTS/summary" target="_blank"><img src="https://img.shields.io/badge/ModelScope-Demo-blue?style=flat-square"></a>
<a href=""><img alt="Python" src="https://img.shields.io/badge/Python-%3E%3D3.9%2C%3C4-aff.svg?style=flat-square&logo=python&logoColor=white"></a>
<a href=""><img alt="OS" src="https://img.shields.io/badge/OS-Linux%2C%20Win%2C%20Mac-pink.svg?style=flat-square"></a>
<a href="https://pypi.org/project/rapidtts/"><img alt="PyPI" src="https://img.shields.io/pypi/v/rapidtts?style=flat-square&logo=pypi&logoColor=white&color=3775A9"></a>
<a href="https://pepy.tech/project/rapidtts"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/rapidtts?period=total&units=abbreviation&left_color=555555&right_color=2F80ED&left_text=downloads"></a>
<a href="https://semver.org/"><img alt="SemVer" src="https://img.shields.io/badge/semver-2.0-3D9970?style=flat-square"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000?style=flat-square"></a>

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
pip install rapidtts
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
- [wetext](https://github.com/pengzhendong/wetext)

## License

RapidTTS 使用 Apache-2.0 License。
