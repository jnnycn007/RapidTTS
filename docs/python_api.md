# Python API

## 基本用法

```python
from rapidtts import RapidTTS, SynthesisRequest, TTSModel

tts = RapidTTS(model=TTSModel.MELO_ONNX)

resp = tts.synthesize(
    SynthesisRequest(
        text="我最近在学习machine learning，希望能够在未来的artificial intelligence领域有所建树。"
    )
)

resp.save("result.wav")
```

## 指定模型目录

```python
tts = RapidTTS(
    model=TTSModel.MELO_ONNX,
    model_root_dir="/path/to/melotts_zh_mix_en_onnx",
)
```

如果不指定 `model_root_dir`，RapidTTS 会使用默认模型目录，并在模型缺失时自动下载。

## 关闭日志

```python
tts = RapidTTS(model=TTSModel.MELO_ONNX, enable_log=False)
```

## 文本归一化

Melo ONNX 默认使用 WeText 文本归一化。也可以显式指定归一化器：

```python
from rapidtts import RapidTTS, TextNormalizerType, TTSModel

tts = RapidTTS(
    model=TTSModel.MELO_ONNX,
    text_normalizer_type=TextNormalizerType.WETEXT,
)
```

可选值包括 `WETEXT`、`LEGACY` 和 `NONE`。

## 请求参数

```python
from rapidtts import SynthesisRequest, TTSLanguage

request = SynthesisRequest(
    text="hello world",
    language=TTSLanguage.EN,
    speed=1.1,
    sample_rate=16000,
)
```

常用字段：

- `text`：待合成文本
- `language`：语言，可选 `ZH`、`EN`、`ZH_MIX_EN`
- `speed`：语速
- `sample_rate`：输出采样率
- `audio_format`：音频格式
- `extras`：后端扩展参数
