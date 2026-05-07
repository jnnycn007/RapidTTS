# 命令行用法

RapidTTS 安装后会提供 `rapidtts` 命令。

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

## 下载模型

下载默认模型：

```bash
rapidtts download melo_onnx
```

下载到自定义目录：

```bash
rapidtts download melo_onnx --save-dir /path/to/melotts_zh_mix_en_onnx
```

关闭进度条：

```bash
rapidtts download melo_onnx --no-progress
```

关闭日志：

```bash
rapidtts download melo_onnx --quiet
```

## 检查安装

```bash
rapidtts check
```

检查自定义模型目录：

```bash
rapidtts check melo_onnx --model-dir /path/to/melotts_zh_mix_en_onnx
```

同时初始化后端：

```bash
rapidtts check --init-backend
```

## 命令速查

```bash
rapidtts download [melo_onnx] [--save-dir DIR] [--no-progress] [--quiet]
rapidtts check [melo_onnx] [--model-dir DIR] [--init-backend] [--quiet]
rapidtts text TEXT OUTPUT [--model melo_onnx] [--model-dir DIR] [--language ZH|EN|ZH_MIX_EN] [--speed SPEED] [--sample-rate SAMPLE_RATE] [--quiet]
```
