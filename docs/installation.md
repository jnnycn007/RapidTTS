# 安装说明

RapidTTS 需要 Python 3.10 或更高版本。

## 从源码安装

```bash
git clone https://github.com/RapidAI/RapidTTS.git
cd RapidTTS
pip install -e .
```

## 开发环境安装依赖

```bash
pip install -r requirements.txt
```

## 检查安装

安装完成后可以运行：

```bash
rapidtts check
```

该命令会检查：

- RapidTTS 包是否可以正常导入
- 关键依赖是否存在
- `config.yaml` 和 `models.yaml` 是否可解析
- 默认模型文件是否存在，SHA256 是否正确

如果还希望验证后端能否初始化：

```bash
rapidtts check --init-backend
```

如果模型文件缺失，先执行：

```bash
rapidtts download melo_onnx
```
