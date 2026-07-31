#!/usr/bin/env python3
"""Generate stable JSON and Markdown indexes from flow/skill frontmatter."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

from pdca_core import repo_root

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def read_asset(root: Path, path: Path, layer: str) -> dict:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path.relative_to(root)}: missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(root)}: frontmatter must be a mapping")
    for field in ("name", "description"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"{path.relative_to(root)}: missing non-empty {field}")
    return {
        "name": data["name"].strip(),
        "description": " ".join(data["description"].split()),
        "invocation": data.get("invocation", "automatic"),
        "layer": layer,
        "file": path.relative_to(root).as_posix(),
    }


def build(root: Path) -> list[dict]:
    assets = [
        *(read_asset(root, path, "flow") for path in sorted((root / "flows").glob("flow-*/SKILL.md"))),
        *(read_asset(root, path, "skill") for path in sorted((root / "skills").glob("**/SKILL.md"))),
    ]
    names = [asset["name"] for asset in assets]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate asset names: {', '.join(duplicates)}")
    return sorted(assets, key=lambda asset: (asset["layer"], asset["name"]))


def render_markdown(assets: list[dict]) -> str:
    lines = [
        "# PDCA Skills Index",
        "",
        "> 由 `scripts/generate-skills-index.py` 从 frontmatter 生成；请勿手工编辑。",
        "",
        "| 类型 | 名称 | 调用 | 文件 | 描述 |",
        "|------|------|------|------|------|",
    ]
    for asset in assets:
        description = asset["description"].replace("|", "\\|")
        lines.append(
            f"| {asset['layer']} | `{asset['name']}` | `{asset['invocation']}` | "
            f"[{asset['file']}]({asset['file']}) | {description} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = repo_root(args.root)
    assets = build(root)
    markdown_text = render_markdown(assets)
    outputs = {root / "SKILLS-INDEX.md": markdown_text}
    if args.check:
        stale = [path.relative_to(root).as_posix() for path, text in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
        if stale:
            print(json.dumps({"valid": False, "stale": stale}, ensure_ascii=False))
            return 1
        print(json.dumps({"valid": True, "asset_count": len(assets)}))
        return 0
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8")
    print(json.dumps({"written": [path.relative_to(root).as_posix() for path in outputs], "asset_count": len(assets)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
