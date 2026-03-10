# Testcase Generator Skill (Standalone)

> 从 Markdown 需求文档自动生成 API / 前端 / 合约 / Unit Test 的测试用例表（Excel）。

## ✨ Features
- 支持四类 Feature：`api` / `frontend` / `contract` / `unit`。
- 每个 Feature 可列多个 Acceptance 场景，脚本会自动生成 Case ID、步骤、期望结果等字段。
- 输出标准 `.xlsx`，可直接导入测试平台或用 Excel 打开。
- 附带简单 Web UI，可在浏览器中粘贴需求并直接下载 Excel。

## 📦 Install
```bash
pip3 install -r requirements.txt
```

## 📄 Requirement Format
按 Feature 使用 Markdown 结构化描述（示例 `samples/requirements-sample.md`）：
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

## 🚀 CLI Usage
```bash
python3 testcase_agent.py \
  --requirements samples/requirements-sample.md \
  --output output/testcases.xlsx \
  --case-prefix QA
```

## 🌐 Web UI
```bash
python3 web_app.py
```
然后访问 <http://localhost:5000>，粘贴 Markdown 需求，可直接下载生成的 Excel。

## 📁 Repo Structure
```
./testcase-generator-skill/
├── README.md
├── generator.py          # 通用解析/生成逻辑
├── requirements.txt
├── testcase_agent.py     # CLI
├── web_app.py            # Flask Web UI
└── samples/
    └── requirements-sample.md
```

## 🧩 Roadmap
- 可扩展更多列（优先级、预期数据等）。
- 可在 Web UI 中支持文件上传/历史记录。
