"""Core logic for testcase generation (shared by CLI & Web)."""
from collections import OrderedDict
from io import BytesIO
from pathlib import Path
from typing import Dict, List
from zipfile import ZIP_DEFLATED, ZipFile
import re
import time
import uuid
import xml.etree.ElementTree as ET

from openpyxl import Workbook

SECTION_RE = re.compile(r"^##\s+(.*)")
FIELD_RE = re.compile(r"^(\w+):\s*(.*)$")

NS_CONTENT = "urn:xmind:xmap:xmlns:content:2.0"
NS_STYLE = "urn:xmind:xmap:xmlns:style:2.0"
NS_COMMENTS = "urn:xmind:xmap:xmlns:comments:2.0"
FO_NS = "http://www.w3.org/1999/XSL/Format"
XHTML_NS = "http://www.w3.org/1999/xhtml"
XLINK_NS = "http://www.w3.org/1999/xlink"
SVG_NS = "http://www.w3.org/2000/svg"

ET.register_namespace("", NS_CONTENT)
ET.register_namespace("fo", FO_NS)
ET.register_namespace("xhtml", XHTML_NS)
ET.register_namespace("xlink", XLINK_NS)
ET.register_namespace("svg", SVG_NS)


def parse_markdown(text: str) -> List[Dict[str, List[str]]]:
    lines = text.splitlines()
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
        "contract": f"1. 准备钱包与资产。\n2. 在合约上执行：{scenario}。\n3. 校验事件/状态/余额",
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


def build_cases(features: List[Dict[str, List[str]]], case_prefix: str = "TC") -> List[Dict[str, object]]:
    cases: List[Dict[str, object]] = []
    prefix = case_prefix.upper()
    for f_idx, feature in enumerate(features, start=1):
        scenarios = feature.get("acceptance") or ["缺少 Acceptance 条目"]
        ftype = feature.get("type", "").lower() or "other"
        data_points = feature.get("data", [])
        constraints = feature.get("constraints", [])
        prereq = feature.get("prerequisites", [])
        for s_idx, scenario in enumerate(scenarios, start=1):
            case_id = f"{prefix}-F{f_idx:02d}-S{s_idx:02d}"
            cases.append(
                {
                    "case_id": case_id,
                    "feature": feature.get("name", f"Feature {f_idx}"),
                    "type": ftype,
                    "scenario": scenario,
                    "preconditions": prereq[:],
                    "steps": build_steps(ftype, scenario, data_points),
                    "expected": build_expected(ftype, scenario),
                    "data_points": data_points[:],
                    "constraints": constraints[:],
                }
            )
    return cases


def cases_to_rows(cases: List[Dict[str, object]]) -> List[List[str]]:
    rows: List[List[str]] = []
    for case in cases:
        rows.append(
            [
                case["case_id"],
                case["feature"],
                case["type"],
                case["scenario"],
                "; ".join(case["preconditions"]) if case["preconditions"] else "",
                case["steps"],
                case["expected"],
                "; ".join(case["data_points"]) if case["data_points"] else "",
                "; ".join(case["constraints"]) if case["constraints"] else "",
            ]
        )
    return rows


def rows_to_excel_bytes(rows: List[List[str]]) -> bytes:
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
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


def save_rows_to_excel(rows: List[List[str]], output_path: Path) -> None:
    data = rows_to_excel_bytes(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)


def _note_block(title: str, items: List[str]) -> List[str]:
    if not items:
        return []
    block = [title]
    block.extend(f"- {item}" for item in items)
    return block


def _format_case_note(case: Dict[str, object]) -> str:
    note_lines = [
        f"Case ID: {case['case_id']}",
        f"类型: {case['type']}",
    ]
    note_lines.extend(_note_block("前置条件", case.get("preconditions", [])))
    note_lines.append("步骤：")
    note_lines.extend(str(case["steps"]).splitlines())
    note_lines.append("期望结果：")
    note_lines.append(str(case["expected"]))
    note_lines.extend(_note_block("数据要点", case.get("data_points", [])))
    note_lines.extend(_note_block("约束", case.get("constraints", [])))
    return "\n".join(line for line in note_lines if line)


def _new_id() -> str:
    return uuid.uuid4().hex


def cases_to_xmind_bytes(cases: List[Dict[str, object]], root_title: str) -> bytes:
    if not cases:
        raise ValueError("no cases to export")

    timestamp = str(int(time.time() * 1000))
    grouped: "OrderedDict[str, List[Dict[str, object]]]" = OrderedDict()
    for case in cases:
        grouped.setdefault(case["feature"], []).append(case)

    root = ET.Element(
        f"{{{NS_CONTENT}}}xmap-content",
        {
            "timestamp": timestamp,
            "version": "2.0",
        },
    )
    root.set("xmlns:fo", FO_NS)
    root.set("xmlns:xhtml", XHTML_NS)
    root.set("xmlns:xlink", XLINK_NS)
    root.set("xmlns:svg", SVG_NS)
    sheet = ET.SubElement(root, f"{{{NS_CONTENT}}}sheet", {"id": _new_id(), "timestamp": timestamp})
    sheet_topic = ET.SubElement(sheet, f"{{{NS_CONTENT}}}topic", {"id": _new_id(), "timestamp": timestamp})
    sheet_title = ET.SubElement(sheet_topic, f"{{{NS_CONTENT}}}title")
    sheet_title.text = root_title
    children = ET.SubElement(sheet_topic, f"{{{NS_CONTENT}}}children")
    topics = ET.SubElement(children, f"{{{NS_CONTENT}}}topics", {"type": "attached"})

    for feature_name, feature_cases in grouped.items():
        feature_topic = ET.SubElement(topics, f"{{{NS_CONTENT}}}topic", {"id": _new_id(), "timestamp": timestamp})
        feature_title = ET.SubElement(feature_topic, f"{{{NS_CONTENT}}}title")
        feature_title.text = f"{feature_name} ({len(feature_cases)})"
        feature_children = ET.SubElement(feature_topic, f"{{{NS_CONTENT}}}children")
        feature_topics = ET.SubElement(feature_children, f"{{{NS_CONTENT}}}topics", {"type": "attached"})
        for case in feature_cases:
            case_topic = ET.SubElement(feature_topics, f"{{{NS_CONTENT}}}topic", {"id": _new_id(), "timestamp": timestamp})
            case_title = ET.SubElement(case_topic, f"{{{NS_CONTENT}}}title")
            case_title.text = f"{case['case_id']} · {case['scenario']}"
            notes = ET.SubElement(case_topic, f"{{{NS_CONTENT}}}notes")
            plain = ET.SubElement(notes, f"{{{NS_CONTENT}}}plain")
            plain.text = _format_case_note(case)

    sheet_name = ET.SubElement(sheet, f"{{{NS_CONTENT}}}title")
    sheet_name.text = root_title

    content_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    styles_xml = (
        f"<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        f"<xmap-styles xmlns=\"{NS_STYLE}\" xmlns:fo=\"{FO_NS}\" xmlns:svg=\"{SVG_NS}\" version=\"2.0\"/>"
    ).encode("utf-8")
    comments_xml = (
        f"<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        f"<comments xmlns=\"{NS_COMMENTS}\" version=\"2.0\"/>"
    ).encode("utf-8")

    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        zf.writestr("content.xml", content_bytes)
        zf.writestr("styles.xml", styles_xml)
        zf.writestr("comments.xml", comments_xml)
    buffer.seek(0)
    return buffer.read()


def save_cases_to_xmind(cases: List[Dict[str, object]], output_path: Path, root_title: str) -> None:
    bytes_data = cases_to_xmind_bytes(cases, root_title=root_title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(bytes_data)


def load_features_from_file(path: Path) -> List[Dict[str, List[str]]]:
    return parse_markdown(path.read_text(encoding="utf-8"))
