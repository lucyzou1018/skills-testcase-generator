# Testcase Generator Skill (Standalone)

> 从 Markdown 需求文档自动生成 API / 前端 / 合约 / Unit Test 的测试用例表（Excel）。

## ✨ Features
- 支持四类 Feature：`api` / `frontend` / `contract` / `unit`。
- 每个 Feature 可列多个 Acceptance 场景，脚本会自动生成 Case ID、步骤、期望结果等字段。
- 输出标准 `.xlsx`，可直接导入测试平台或用 Excel 打开。
- 提供 CLI + Flask Web UI；已适配 Vercel serverless。

## 📦 Install
```bash
pip3 install -r requirements.txt
```

## 📄 Requirement Format
按 Feature 使用 Markdown 结构化描述（示例 `samples/requirements-sample.md`）。

## 🚀 CLI
```bash
python3 testcase_agent.py \
  --requirements samples/requirements-sample.md \
  --output output/testcases.xlsx \
  --case-prefix QA
```

## 🌐 Web UI（本地）
```bash
python3 web_app.py
```
访问 <http://localhost:5000> 粘贴 Markdown 需求，即可下载 Excel。

## ☁️ Vercel 部署
1. 安装依赖并登录 Vercel：
   ```bash
   npm i -g vercel    # 如未安装
   vercel login
   ```
2. 在仓库根目录执行：
   ```bash
   vercel --prod
   ```
   - `vercel.json` 已映射所有路由到 `api/index.py`。
   - `api/index.py` 通过 `vercel-wsgi` 适配 Flask -> Serverless。
3. 部署完成后，访问 Vercel 分配的域名即可使用在线版本。

## 📁 Repo Structure
```
./testcase-generator-skill/
├── README.md
├── api/
│   └── index.py            # Vercel serverless 入口
├── generator.py
├── requirements.txt
├── testcase_agent.py
├── web_app.py
└── samples/
    └── requirements-sample.md
```

## 🧩 Roadmap
- 扩展更多列（优先级、预期数据）。
- Web UI 支持文件上传、历史列表。
