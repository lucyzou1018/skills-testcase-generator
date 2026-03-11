#!/usr/bin/env python3
"""Simple Flask UI for testcase generator."""
from datetime import datetime
from io import BytesIO

from flask import Flask, render_template_string, request, send_file, flash

from generator import (
    build_cases,
    cases_to_rows,
    cases_to_xmind_bytes,
    parse_markdown,
    rows_to_excel_bytes,
)

app = Flask(__name__)
app.secret_key = "testcase-generator-secret"

TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Testcase Generator</title>
  <style>
    body { font-family: 'Inter','PingFang SC',sans-serif; background:#0f1117; color:#f5f6ff; margin:0; padding:24px; }
    .container { max-width: 960px; margin: 0 auto; }
    textarea { width: 100%; height: 400px; border-radius: 12px; border: 1px solid #303450; background:#15172b; color:#f5f6ff; padding:14px; font-family: 'Fira Code',monospace; }
    input[type=text] { border-radius: 8px; border:1px solid #303450; background:#15172b; color:#f5f6ff; padding:10px; }
    button { background:#17c0ff; color:#05060c; border:none; border-radius:999px; padding:12px 28px; font-size:15px; cursor:pointer; }
    button:hover { background:#15abd6; }
    .flash { margin:12px 0; padding:12px; border-radius:10px; background:#ff8a6522; border-left:4px solid #ff8a65; }
    .format-select { margin:16px 0; }
    label { display:inline-flex; align-items:center; gap:6px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Testcase Generator · Web UI</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for msg in messages %}<div class="flash">{{ msg }}</div>{% endfor %}
      {% endif %}
    {% endwith %}
    <form method="post">
      <label>Case ID Prefix:&nbsp;<input type="text" name="prefix" value="{{ prefix }}" /></label>
      <div class="format-select">
        <strong>导出格式：</strong>
        <label><input type="radio" name="format" value="excel" {% if export_format == 'excel' %}checked{% endif %}/> Excel (.xlsx)</label>
        <label><input type="radio" name="format" value="xmind" {% if export_format == 'xmind' %}checked{% endif %}/> XMind (.xmind)</label>
      </div>
      <textarea name="requirements" placeholder="在此粘贴 Markdown 需求文档" required>{{ requirements }}</textarea>
      <p></p>
      <button type="submit">生成</button>
    </form>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    prefix = request.form.get("prefix", "TC")
    requirements = request.form.get("requirements", "")
    export_format = request.form.get("format", "excel")
    if request.method == "POST":
        if not requirements.strip():
            flash("请粘贴 Markdown 需求文档")
            return render_template_string(TEMPLATE, prefix=prefix, requirements=requirements, export_format=export_format)
        features = parse_markdown(requirements)
        if not features:
            flash("未解析到 Feature。请确认文档使用 `## Feature` + Acceptance 列表。")
            return render_template_string(TEMPLATE, prefix=prefix, requirements=requirements, export_format=export_format)
        cases = build_cases(features, case_prefix=prefix)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        root_title = f"Testcases-{prefix.upper()}"

        if export_format == "xmind":
            xmind_bytes = cases_to_xmind_bytes(cases, root_title=root_title)
            filename = f"testcases-{timestamp}.xmind"
            return send_file(
                BytesIO(xmind_bytes),
                mimetype="application/vnd.xmind.workbook",
                as_attachment=True,
                download_name=filename,
            )

        rows = cases_to_rows(cases)
        excel_bytes = rows_to_excel_bytes(rows)
        filename = f"testcases-{timestamp}.xlsx"
        return send_file(
            BytesIO(excel_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )
    return render_template_string(TEMPLATE, prefix=prefix, requirements=requirements, export_format=export_format)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
