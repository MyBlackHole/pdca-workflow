#!/usr/bin/env python3
"""本体-代码版本联动：追踪每个本体节点对应的代码版本。

用法：
  python3 scripts/ontology-version-link.py --ontology-dir ontology --source src/
  python3 scripts/ontology-version-link.py --ontology-dir ontology --source src/ --update
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def get_git_info(file_path: Path) -> dict:
    """获取文件的 Git 版本信息。"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%ct|%s", "--", str(file_path)],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT)
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|", 2)
            return {"commit": parts[0], "timestamp": parts[1], "message": parts[2] if len(parts) > 2 else ""}
    except Exception:
        pass
    return {"commit": "", "timestamp": "", "message": ""}


def link_versions(ont_dir: Path, source_dir: Path) -> list[dict]:
    """为本体节点添加 code_version 字段。"""
    linked = []
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
        git_info = get_git_info(md)
        linked.append({
            "ontology_id": oid,
            "ontology_file": str(md),
            "code_version": git_info,
            "source_dir": str(source_dir)
        })

    return linked


def main() -> int:
    ap = argparse.ArgumentParser(description="本体-代码版本联动")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--source", type=Path, default=ROOT / "src")
    ap.add_argument("--update", action="store_true", help="更新 frontmatter 中的 code_version")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    linked = link_versions(args.ontology_dir, args.source)

    if args.update:
        for entry in linked:
            md_path = Path(entry["ontology_file"])
            text = md_path.read_text(encoding="utf-8")
            fm = {}
            if text.startswith("---"):
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                    except Exception:
                        pass

            if "code_version" not in fm:
                fm["code_version"] = entry["code_version"]["commit"]
                new_fm = yaml.dump(fm, default_flow_style=False, allow_unicode=True)
                new_text = f"---\n{new_fm}---\n" + text.split("---", 2)[2] if text.startswith("---") else text
                md_path.write_text(new_text, encoding="utf-8")

    report = {
        "linked_count": len(linked),
        "linked": linked[:20],  # 只显示前20个
        "all_linked": len(linked) == len([f for f in args.ontology_dir.rglob("*.md")])
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
