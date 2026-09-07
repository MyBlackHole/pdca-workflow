#!/usr/bin/env python3
"""影响分析：代码变更时自动识别影响的本体节点。

用法：
  python3 scripts/ontology-impact.py --changed-files src/file1.py,src/file2.py
  python3 scripts/ontology-impact.py --changed-files src/file1.py --ontology-dir ontology
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def find_affected_ontology(changed_files: list[str], ont_dir: Path) -> list[dict]:
    """分析变更文件，找到引用的本体节点。"""
    affected = []
    changed_paths = set(changed_files)

    # 建立文件名到本体节点的映射
    for md in sorted(ont_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        fm = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                except Exception:
                    pass

        oid = fm.get("id", str(md))
        # 查找正文中对变更文件的引用
        refs = re.findall(r'(src/[^`\s]+\.(py|cpp|go|rs|c))', text)
        refs += re.findall(r'`([^`]+\.(py|cpp|go|rs|c))`', text)
        refs = [r[0] if isinstance(r, tuple) else r for r in refs]

        for ref in refs:
            for changed in changed_files:
                if changed in ref or ref in changed:
                    affected.append({
                        "changed_file": changed,
                        "ontology_id": oid,
                        "ontology_file": str(md),
                        "reference": ref,
                        "impact_type": "direct_reference"
                    })

    return affected


def main() -> int:
    ap = argparse.ArgumentParser(description="代码变更影响分析")
    ap.add_argument("--changed-files", nargs="+", required=True, help="变更的文件路径列表")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    affected = find_affected_ontology(args.changed_files, args.ontology_dir)

    report = {
        "changed_files": args.changed_files,
        "affected_count": len(affected),
        "affected": affected
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"# 影响分析报告\n\n变更文件: {args.changed_files}\n\n影响本体节点: {len(affected)}\n\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
