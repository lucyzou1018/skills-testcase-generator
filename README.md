# Testcase Generator Skill (Standalone)

> 从 Markdown 需求文档自动生成 API / 前端 / 合约 / Unit Test 的测试用例表（Excel）。

## ✨ Features
- 支持四类 Feature：`api` / `frontend` / `contract` / `unit`。
- 每个 Feature 可列多个 Acceptance 场景，脚本会自动生成 Case ID、步骤、期望结果等字段。
- 输出标准 `.xlsx`，可直接导入测试平台或用 Excel 打开。

## 📦 Install
```bash
pip3 install --user openpyxl
```

## 📄 Requirement Format
按 Feature 使用 Markdown 结构化描述：
```
## 登录接口
Type: api
Summary: xxx
Prerequisites:
- 条件1
Acceptance:
- 场景1
- 场景2
Constraints:
- 约束1
Data:
- username: string / required
```
*字段说明：*
- `Type`（必填）：api/frontend/contract/unit
- `Acceptance`（必填）：多条用例场景
- 其余（Summary/Prerequisites/Constraints/Data）可选。

完整示例：`samples/requirements-sample.md`

## 🚀 Usage
```bash
python3 testcase_agent.py \
  --requirements samples/requirements-sample.md \
  --output output/testcases.xlsx \
  --case-prefix QA   # 可选，默认 TC
```
运行后会在 `output/` 下生成 Excel：
- 列包含：Case ID / Feature / Type / Scenario / Preconditions / Steps / Expected / Data Points / Constraints

## 📁 Repo Structure
```
./testcase-generator-skill/
├── README.md
├── testcase_agent.py
└── samples/
    └── requirements-sample.md
```

## 🧩 Roadmap
- 可扩展更多列（如优先级、预期数据）。
- 可在未来接入 Web UI，将 Markdown 粘贴后直接下载 Excel。
