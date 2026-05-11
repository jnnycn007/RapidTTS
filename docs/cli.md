# 命令行用法

RapidTTS 安装后会提供 `rapidtts` 命令。

## 命令速查

```bash
rapidtts download [kokoro_onnx] [--save-dir DIR] [--no-progress] [--quiet]
rapidtts check [kokoro_onnx] [--model-dir DIR] [--init-backend] [--quiet]
rapidtts info [kokoro_onnx] [--model-dir DIR] [--quiet]
rapidtts voices [kokoro_onnx] [--model-dir DIR] [--quiet]
rapidtts text TEXT OUTPUT [--model kokoro_onnx] [--model-dir DIR] [--language ZH|EN|ZH_MIX_EN] [--speed SPEED] [--sample-rate SAMPLE_RATE] [--quiet]
```

## 检查安装

```bash
rapidtts check
```

检查自定义模型目录：

```bash
rapidtts check kokoro_onnx --model-dir /path/to/kokoro_onnx
```

同时初始化后端：

```bash
rapidtts check --init-backend
```

## 查看模型能力

查看模型支持的语言、默认语言、音色数量和默认音色：

```bash
rapidtts info kokoro_onnx
```

查看模型可用音色：

```bash
rapidtts voices kokoro_onnx
```

Kokoro ONNX 是默认后端，建议安装：

```bash
pip install "rapidtts[kokoro]"
```

MeloTTS 后端需要额外依赖：

```bash
pip install "rapidtts[melo]"
rapidtts info melo_onnx
rapidtts voices melo_onnx
```

## 下载模型

下载默认模型：

```bash
rapidtts download kokoro_onnx
```

下载到自定义目录：

```bash
rapidtts download kokoro_onnx --save-dir /path/to/kokoro_onnx
```

关闭进度条：

```bash
rapidtts download kokoro_onnx --no-progress
```

关闭日志：

```bash
rapidtts download kokoro_onnx --quiet
```

## 文本合成

```bash
rapidtts text "你好，RapidTTS" outputs/1.wav
```

指定语言：

```bash
rapidtts text "hello world" outputs/en.wav --language EN
```

指定语速和采样率：

```bash
rapidtts text "你好，RapidTTS" outputs/1.wav --speed 1.2 --sample-rate 16000
```

使用自定义模型目录：

```bash
rapidtts text "你好，RapidTTS" outputs/1.wav --model-dir /path/to/melotts_zh_mix_en_onnx
```

关闭 RapidTTS 日志：

```bash
rapidtts text "你好，RapidTTS" outputs/1.wav --quiet
```
