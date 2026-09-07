#!/usr/bin/env python3
"""持续监控与告警：检测本体-代码漂移，本体过时自动告警。

用法：
  python3 scripts/ontology-drift-monitor.py --ontology-dir ontology --source src/
  python3 scripts/ontology-drift-monitor.py --ontology-dir ontology --source src/ --ci
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def check_drift(ont_dir: Path, source_dir: Path) -> list[dict]:
    """检测本体-代码漂移：本体引用的代码文件是否仍然存在。"""
    drifts = []
    if not source_dir.is_dir():
        return drifts

    source_files = {f.name for f in source_dir.rglob("*") if f.is_file()}
    source_paths = set(str(f) for f in source_dir.rglob("*") if f.is_file())

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

        # 检查正文中的代码引用
        code_refs = re.findall(r'(?:file|Source|source)\s*[:=]\s*`([^`]+)`', text)
        code_refs += re.findall(r'`(src/[^`]+)`', text)
        code_refs += re.findall(r'(`[^`]+\.(py|cpp|go|rs|c)`)', text)

        for ref in code_refs:
            ref = ref.strip().strip('`')
            if not ref.startswith("src/") and not ref.startswith("ontology/"):
                ref = f"src/{ref}"
            ref_path = ROOT / ref
            if not ref_path.is_file():
                oid = fm.get("id", str(md))
                drifts.append({
                    "ontology_id": oid,
                    "missing_reference": ref,
                    "ontology_file": str(md),
                    "type": "missing_code_file"
                })

        # 检查 Source: 行号是否仍然有效
        source_lines = re.findall(r'Source:\s*(.+)', text)
        for src in source_lines:
            src = src.strip()
            if src.startswith("src/") or src.startswith("ontology/"):
                ref_path = ROOT / src.split(":")[0] if ":" in src else ROOT / src
                if not ref_path.is_file():
                    oid = fm.get("id", str(md))
                    drifts.append({
                        "ontology_id": oid,
                        "missing_reference": src,
                        "ontology_file": str(md),
                        "type": "missing_source_reference"
                    })

    return drifts


def main() -> int:
    ap = argparse.ArgumentParser(description="本体-代码漂移监控")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--source", type=Path, default=None)
    ap.add_argument("--ci", action="store_true", help="CI模式：发现漂移时非0退出")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    source = args.source or ROOT / "src"
    drifts = check_drift(args.ontology_dir, source)

    report = {
        "drifts_found": len(drifts),
        "drifts": drifts,
        "status": "CLEAN" if not drifts else "DRIFT_DETECTED"
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"# 漂移报告\n\n状态: {report['status']}\n\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.ci and drifts:
        print(f"\nDRIFT DETECTED: {len(drifts)} 个漂移", file=sys.stderr)
        return 1
    if not drifts:
        print("OK: 无漂移", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
