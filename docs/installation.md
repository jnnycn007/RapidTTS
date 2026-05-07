# 安装说明

## 从源码安装

```bash
pip install rapidtts
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
