# 开发说明

## 安装开发依赖

```bash
pip install -r requirements.txt
```

## 运行测试

运行全部测试：

```bash
python -m pytest tests -q
```

只运行 CLI 测试：

```bash
python -m pytest tests/test_cli.py -q
```

## 项目结构

```text
rapidtts/
  backends/        # 后端实现
  common/          # 通用工具，如下载、日志、音频处理
  configs/         # 默认配置和模型元数据
  core/            # 核心 API、请求、响应、模型资产管理
  cli.py           # 命令行入口
tests/             # 单元测试
docs/              # 文档
```

## CLI 入口

`setup.py` 中注册了命令行入口：

```python
entry_points={"console_scripts": ["rapidtts=rapidtts.cli:main"]}
```

因此安装后可以直接使用：

```bash
rapidtts --help
```
