# RapidTTS

RapidTTS 是一个轻量级文本转语音工具，面向本地快速推理。当前默认后端是导出为 ONNX 的 MeloTTS。

## 安装

```bash
pip install rapidtts
```

从源码安装：

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

## 常用命令

```bash
rapidtts download melo_onnx
rapidtts check
rapidtts text "你好，RapidTTS" outputs/1.wav
```

## 模型文件

默认模型文件会在未指定模型目录时下载到库安装目录下，并使用 `models.yaml` 中声明的 SHA256 进行校验。

自定义下载目录：

```bash
rapidtts download melo_onnx --save-dir /path/to/melotts_zh_mix_en_onnx
```

自定义推理模型目录：

```bash
rapidtts text "你好，RapidTTS" outputs/1.wav --model-dir /path/to/melotts_zh_mix_en_onnx
```

## License

RapidTTS 使用 Apache-2.0 License。
