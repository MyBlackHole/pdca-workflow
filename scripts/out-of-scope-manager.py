#!/usr/bin/env python3
"""out-of-scope 知识库管理器（T0266）。

维护被拒绝特性请求的概念级聚合记录，供 triage dedup surfacing。
一个概念一个文件：ontology/domain/out-of-scope-<concept>.md。
同一概念的后续拒绝追加到已有文件的 ## Prior requests，不新建文件。

用法：
  out-of-scope-manager.py add --concept <kebab> --reason <durable reason> \
      --request "<issue/PR 描述>" [--implemented]
  out-of-scope-manager.py check --concept <kebab>
  out-of-scope-manager.py list
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def slugify(concept: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", concept.lower()).strip("-")
    if not slug:
        raise SystemExit("concept 不能为空")
    return slug


def title_case(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def concept_file(out_dir: Path, concept: str) -> Path:
    return out_dir / f"{slugify(concept)}.md"


def existing_prior_requests(out_dir: Path, concept: str) -> list[str]:
    """返回已有文件中 ## Prior requests 段下的历史请求列表。"""
    target = concept_file(out_dir, concept)
    if not target.is_file():
        return []
    text = target.read_text(encoding="utf-8")
    section = text.split("## Prior requests", 1)
    if len(section) < 2:
        return []
    return [line.strip() for line in section[1].splitlines() if line.strip().startswith("- ")]


def cmd_add(args: argparse.Namespace) -> int:
    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.implemented:
        # 反污染：已实现的拒绝不是拒绝，写入会污染 dedup 造成假拒绝
        print(json.dumps(
            {"status": "rejected-implemented", "concept": args.concept,
             "note": "已实现的功能不是 out-of-scope；禁止写入，避免污染 dedup"},
            ensure_ascii=False,
        ))
        return 0

    slug = slugify(args.concept)
    target = concept_file(out_dir, args.concept)
    if target.is_file():
        prior = existing_prior_requests(out_dir, args.concept)
        if args.request not in prior:
            with target.open("a", encoding="utf-8") as f:
                f.write(f"- {args.request}\n")
        print(json.dumps(
            {"status": "appended", "file": f"{slug}.md", "concept": args.concept},
            ensure_ascii=False,
        ))
        return 0

    # 新概念：创建概念级文件
    content = (
        f"# {title_case(slug)}\n\n"
        f"## Why this is out of scope\n\n"
        f"{args.reason}\n\n"
        f"## Prior requests\n\n"
        f"- {args.request}\n"
    )
    target.write_text(content, encoding="utf-8")
    print(json.dumps(
        {"status": "created", "file": f"{slug}.md", "concept": args.concept},
        ensure_ascii=False,
    ))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    out_dir = Path(args.dir)
    target = concept_file(out_dir, args.concept)
    if not target.is_file():
        print(json.dumps({"match": False, "concept": args.concept}, ensure_ascii=False))
        return 0
    text = target.read_text(encoding="utf-8")
    section = text.split("## Why this is out of scope", 1)
    reason = section[1].strip() if len(section) > 1 else ""
    print(json.dumps(
        {"match": True, "file": target.name, "concept": args.concept, "reason": reason},
        ensure_ascii=False,
    ))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    out_dir = Path(args.dir)
    files = sorted(p.name for p in out_dir.glob("*.md"))
    print(json.dumps({"files": files}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="ontology/domain/out-of-scope", help="out-of-scope 目录")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="记录一次 wontfix 拒绝（概念级聚合）")
    add.add_argument("--concept", required=True)
    add.add_argument("--reason", required=True)
    add.add_argument("--request", required=True)
    add.add_argument("--implemented", action="store_true",
                     help="该拒绝是因为已实现——禁止写入 out-of-scope")
    add.set_defaults(func=cmd_add)

    check = sub.add_parser("check", help="查是否已有同概念拒绝")
    check.add_argument("--concept", required=True)
    check.set_defaults(func=cmd_check)

    list_ = sub.add_parser("list", help="列出所有 out-of-scope 概念")
    list_.set_defaults(func=cmd_list)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
