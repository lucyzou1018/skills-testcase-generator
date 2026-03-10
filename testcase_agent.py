#!/usr/bin/env python3
"""Standalone Testcase Generator
Usage:
  python3 testcase_agent.py --requirements requirements.md --output cases.xlsx
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List

from openpyxl import Workbook

SECTION_RE = re.compile(r"^##\s+(.*)")
FIELD_RE = re.compile(r"^(\w+):\s*(.*)$")


def parse_requirements(path: Path) -> List[Dict[str, List[str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    features: List[Dict[str, List[str]]] = []
    current: Dict[str, List[str]] | None = None
    current_list: str | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        section = SECTION_RE.match(line)
        if section:
            if current:
                features.append(current)
            current = {
                "name": section.group(1).strip(),
                "type": "",
                "summary": "",
                "prerequisites": [],
                "acceptance": [],
                "constraints": [],
                "data": [],
            }
            current_list = None
            continue
        if current is None:
            continue
        field = FIELD_RE.match(line)
        if field:
            key = field.group(1).lower()
            value = field.group(2).strip()
            if key == "type":
                current["type"] = value.lower()
            elif key == "summary":
                current["summary"] = value
            current_list = None
            continue
        key_lower = line.lower()
        if key_lower.startswith("prerequisites:"):
            current_list = "prerequisites"
            continue
        if key_lower.startswith("acceptance:"):
            current_list = "acceptance"
            continue
        if key_lower.startswith("constraints:"):
            current_list = "constraints"
            continue
        if key_lower.startswith("data:"):
            current_list = "data"
            continue
        if line.startswith("- ") and current_list:
            current[current_list].append(line[2:].strip())

    if current:
        features.append(current)
    return features


def build_steps(feature_type: str, scenario: str, data_points: List[str]) -> str:
    data_hint = f"准备数据：{'; '.join(data_points)}" if data_points else "准备所需数据"
    mapping = {
        "api": f"1. {data_hint}。\n2. 调用接口执行：{scenario}。\n3. 校验 HTTP 状态与字段",
        "frontend": f"1. 打开页面。\n2. 完成交互：{scenario}。\n3. 检查 UI 元素/文案",
        "contract": f"1. 准备钱包与资产。\n2. 在合约上执行：{scenario}。\n3. 校验事件、状态、余额",
        "unit": f"1. {data_hint}。\n2. 调用函数执行：{scenario}。\n3. 断言返回值/异常",
    }
    return mapping.get(feature_type, f"1. {data_hint}。\n2. 执行：{scenario}。\n3. 验证系统表现")


def build_expected(feature_type: str, scenario: str) -> str:
    mapping = {
        "api": f"接口返回符合 {scenario} 描述的状态/数据",
        "frontend": f"UI 展示与 {scenario} 一致，元素与文案正确",
        "contract": f"链上状态/事件符合 {scenario} 的预期",
        "unit": f"函数执行结果满足 {scenario} 的断言",
    }
    return mapping.get(feature_type, f"系统行为满足 {scenario} 的预期")


def to_excel(rows: List[List[str]], output_path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "testcases"
    headers = [
        "Case ID",
        "Feature",
        "Type",
        "Scenario",
        "Preconditions",
        "Steps",
        "Expected Result",
        "Data Points",
        "Constraints",
    ]
    ws.append(headers)
    for row in rows:
        ws.append(row)
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max(12, max_len + 2), 80)
    wb.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone Testcase Generator")
    parser.add_argument("--requirements", required=True, help="Markdown requirement file")
    parser.add_argument("--output", required=True, help="Output Excel (.xlsx)")
    parser.add_argument("--case-prefix", default="TC", help="Case ID prefix (default TC)")
    args = parser.parse_args()

    req_path = Path(args.requirements)
    if not req_path.exists():
        raise SystemExit(f"❌ requirements file not found: {req_path}")
    features = parse_requirements(req_path)
    if not features:
        raise SystemExit("❌ no features parsed. 请确保文档包含 `## Feature` 与 `Acceptance:` 列表。")

    rows: List[List[str]] = []
    prefix = args.case_prefix.upper()
    for f_idx, feature in enumerate(features, start=1):
        scenarios = feature.get("acceptance") or ["缺少 Acceptance 条目"]
        ftype = feature.get("type", "").lower() or "other"
        data_points = feature.get("data", [])
        constraints = feature.get("constraints", [])
        prereq = feature.get("prerequisites", [])
        for s_idx, scenario in enumerate(scenarios, start=1):
            case_id = f"{prefix}-F{f_idx:02d}-S{s_idx:02d}"
            rows.append([
                case_id,
                feature.get("name", f"Feature {f_idx}"),
                ftype,
                scenario,
                "; ".join(prereq) if prereq else "",
                build_steps(ftype, scenario, data_points),
                build_expected(ftype, scenario),
                "; ".join(data_points) if data_points else "",
                "; ".join(constraints) if constraints else "",
            ])

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    to_excel(rows, out_path)
    print(f"✅ Generated {len(rows)} cases → {out_path}")


if __name__ == "__main__":
    main()
