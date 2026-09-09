#!/usr/bin/env python3
# 本体投射[T2081]：ontology:domain/skill-research（research强制网络查询门禁）；本体是源、代码是投射。
"""research强制网络查询门禁（T2081）。

口径：research-report参考资料≥2 URL，且正文Source:行至少1条httpURL，否则阻断。
用法：check-research-web-evidence.py --report <research-report.md>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://\S+")


def check(report: Path) -> dict:
    text = report.read_text(encoding="utf-8")
    urls = URL_RE.findall(text)
    source_lines = [ln for ln in text.splitlines() if "Source:" in ln]
    http_source = [ln for ln in source_lines if URL_RE.search(ln)]
    ok = len(set(urls)) >= 2 and len(http_source) >= 1
    return {
        "report": str(report),
        "url_count": len(set(urls)),
        "http_source_lines": len(http_source),
        "required": {"urls>=2": True, "http_source>=1": True},
        "valid": ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.report.is_file():
        print(json.dumps({"valid": False, "error": "REPORT_MISSING"}), file=sys.stderr)
        return 2
    result = check(args.report)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
