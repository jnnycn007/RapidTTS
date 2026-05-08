# 模型文件

默认模型文件托管在 ModelScope：

```text
https://www.modelscope.cn/models/RapidAI/RapidTTS/tree/master/models/melotts/onnx
```

模型元数据声明在：

```text
rapidtts/configs/models.yaml
```

其中包含：

- 下载地址 `base_url`
- 默认本地目录 `local_dir`
- 文件列表
- 每个文件的 SHA256

## 支持的模型和语言

|模型名称|支持语言|备注|
|:---:|:---:|:---:|
|[MeloTTS](https://github.com/myshell-ai/MeloTTS)|ZH_MIX_EN|中英混合|

## 默认下载目录

如果用户没有指定模型目录，RapidTTS 会把默认模型下载到库安装目录下：

```text
<rapidtts package root>/models/melotts_zh_mix_en_onnx
```

`models.yaml` 中的相对路径会以 `rapidtts` 包目录作为基准，而不是当前工作目录。

## SHA256 校验

每个模型文件下载完成后都会计算 SHA256，并与 `models.yaml` 中声明的值比较。

如果本地文件存在且 SHA256 正确，会直接复用。

如果文件缺失或 SHA256 不一致，会重新下载。

如果重新下载后 SHA256 仍不一致，会删除该文件并抛出错误。

## 手动下载

```bash
rapidtts download melo_onnx
```

下载到自定义目录：

```bash
rapidtts download melo_onnx --save-dir /path/to/melotts_zh_mix_en_onnx
```

检查模型文件：

```bash
rapidtts check melo_onnx
```
