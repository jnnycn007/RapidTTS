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

## 文本归一化与风险检测

文本归一化规则位于 `rapidtts/common/text/rules.py`。这些规则用于在进入 TTS 前处理高置信业务文本，例如车牌、订单号、房号、金额、百分比、状态码、存储单位和中英混合缩写。

`rapidtts/common/text/risk.py` 提供风险检测能力。它不修改文本，也不会参与线上 TTS 生成流程；它只用于开发和测试阶段，扫描归一化后的文本里是否还残留容易被 TTS 读错的形态。

当前风险检测会关注这些残留：

- 车牌号，例如 `京A86F29`
- ISO 日期，例如 `2026-05-08`
- 人民币金额，例如 `￥99.9`
- 百分比，例如 `6.3%`
- 存储单位，例如 `12.3GB`
- 房号、订单号、状态码等上下文编号
- 股票符号，例如 `A股`
- 紧凑大写缩写或 ID，例如 `API`、`AB20260508`
- 长数字串，例如手机号、验证码

### 添加归一化样例

真实样例集中维护在 `tests/fixtures/text_normalization_cases.json`。新增样例时添加一条记录：

```json
{
  "id": "order_id_and_rmb",
  "text": "订单ID是AB20260508，金额是￥99.9。",
  "legacy": "订单I D 是A B 二 零 二 六 零 五 零 八，金额是九十九元九角。"
}
```

然后运行：

```bash
python -m pytest tests/test_text_normalization.py tests/test_text_risk.py -q
```

`tests/test_text_normalization.py` 会检查归一化结果是否等于 `legacy`，并用 `detect_risky_tokens()` 断言归一化后的文本不再残留高风险 token。

### 手动检查文本

开发时也可以直接调用默认归一化器和风险检测：

```python
from rapidtts import TextNormalizerType
from rapidtts.common.text.normalization import create_text_normalizer
from rapidtts.common.text.risk import detect_risky_tokens

text = "订单ID是AB20260508，金额是￥99.9。"
normalizer = create_text_normalizer(TextNormalizerType.WETEXT)
normalized = normalizer.normalize(text)

for risk in detect_risky_tokens(normalized):
    print(risk.rule, risk.token, risk.reason)
```

如果输出为空，表示当前检测规则没有发现明显高风险残留。也可以对原始文本调用 `detect_risky_tokens()`，用于确认某类新样例是否会被风险检测捕获。

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
