#!/usr/bin/env python3
"""Standalone CLI entry for testcase generator."""
import argparse
from pathlib import Path

from generator import load_features_from_file, build_rows, save_rows_to_excel


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone Testcase Generator")
    parser.add_argument("--requirements", required=True, help="Markdown requirement file")
    parser.add_argument("--output", required=True, help="Output Excel (.xlsx)")
    parser.add_argument("--case-prefix", default="TC", help="Case ID prefix (default TC)")
    args = parser.parse_args()

    req_path = Path(args.requirements)
    if not req_path.exists():
        raise SystemExit(f"❌ requirements file not found: {req_path}")

    features = load_features_from_file(req_path)
    if not features:
        raise SystemExit("❌ no features parsed. 请确保文档包含 `## Feature` 与 `Acceptance:` 列表。")

    rows = build_rows(features, case_prefix=args.case_prefix)
    save_rows_to_excel(rows, Path(args.output))
    print(f"✅ Generated {len(rows)} cases → {args.output}")


if __name__ == "__main__":
    main()
