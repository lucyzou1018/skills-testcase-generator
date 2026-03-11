#!/usr/bin/env python3
"""Standalone CLI entry for testcase generator."""
import argparse
from pathlib import Path

from generator import (
    build_cases,
    cases_to_rows,
    load_features_from_file,
    save_cases_to_xmind,
    save_rows_to_excel,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone Testcase Generator")
    parser.add_argument("--requirements", required=True, help="Markdown requirement file")
    parser.add_argument("--output", help="Output Excel (.xlsx)")
    parser.add_argument("--xmind-output", help="Output XMind (.xmind)")
    parser.add_argument("--case-prefix", default="TC", help="Case ID prefix (default TC)")
    args = parser.parse_args()

    if not args.output and not args.xmind_output:
        raise SystemExit("❌ 请至少指定 --output 或 --xmind-output 之一")

    req_path = Path(args.requirements)
    if not req_path.exists():
        raise SystemExit(f"❌ requirements file not found: {req_path}")

    features = load_features_from_file(req_path)
    if not features:
        raise SystemExit("❌ no features parsed. 请确保文档包含 `## Feature` 与 `Acceptance:` 列表。")

    cases = build_cases(features, case_prefix=args.case_prefix)
    delivered = []

    if args.output:
        rows = cases_to_rows(cases)
        save_rows_to_excel(rows, Path(args.output))
        delivered.append(f"Excel → {args.output}")

    if args.xmind_output:
        save_cases_to_xmind(cases, Path(args.xmind_output), root_title=req_path.stem or "Testcases")
        delivered.append(f"XMind → {args.xmind_output}")

    print(f"✅ Generated {len(cases)} cases: {'; '.join(delivered)}")


if __name__ == "__main__":
    main()
