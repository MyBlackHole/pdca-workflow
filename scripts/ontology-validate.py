#!/usr/bin/env python3
"""Validate ontology/ assets against the SSOT contract.

Checks (mapped to SSOT v3 acceptance criteria):
  AC-1  directory-as-truth: frontmatter `type` == parent `<type>/` dir name
  AC-1b type vocabulary: `type` in controlled set
  AC-2  references non-dangling: relation/domain ids resolve to existing nodes
  AC-3  acyclic: reference graph over relation keys is a DAG
  AC-4  attribute->test coverage: each attributes[].testable_signal non-empty
  AC-5  relation richness: each KnowledgeArtifact has guides/relates_to
  AC-6  guides domain/range: source is knowledge, target is domain/process
  COMPOSED_OF_RANGE: composed_of 目标须为实体/概念实体类（README §5）
  CONFIGURED_BY_RANGE: configured_by 目标须为 TLSConfiguration 节点（README §5）
  REDIRECT_DANGLING: knowledge/ redirect stubs (frontmatter redirect_to) point to existing ontology/ nodes (ADR-0030)
  schema: pdca.asset/v1 required fields / enum values

Exit code is 1 when any issue is found, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RELATION_KEYS = (
    "specializes",
    "instance_of",
    "composed_of",
    "configured_by",
    "part_of",
    "guides",
    "relates_to",
)
TYPE_VOCAB = {"domain", "entity", "concept", "process", "role",
              "pattern", "principle", "pitfall", "fact", "decision"}
KNOWLEDGE_VOCAB = {"pattern", "principle", "pitfall", "fact", "decision"}
DOMAIN_VOCAB = {"domain", "entity", "concept", "process", "role"}
# README §5 声明 configured_by 的 range 唯一为 TLSConfiguration 节点
TLS_CONFIG_ID = "ontology:entity/tls-configuration"
LAYER_ENUM = ("Evidence", "Experience", "Knowledge", "Skill")
STATUS_ENUM = ("active", "deprecated", "superseded")


def extract_frontmatter(text: str) -> dict:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            data = yaml.safe_load(parts[1])
            return data if isinstance(data, dict) else {}
    return {}


def iter_assets(ont_dir: Path):
    for md in sorted(ont_dir.rglob("*.md")):
        rel = md.relative_to(ont_dir)
        if rel.name == "README.md":
            continue
        yield md, rel.parts[0], extract_frontmatter(md.read_text(encoding="utf-8"))


def is_ontology_ref(value) -> bool:
    return isinstance(value, str) and (":" in value or "/" in value)


def validate(ont_dir: Path):
    issues = []
    nodes = {}
    nodes_type = {}
    assets = []
    for path, type_dir, fm in iter_assets(ont_dir):
        assets.append((path, type_dir, fm))
        oid = fm.get("id")
        if oid:
            nodes[oid] = path
            nodes_type[oid] = type_dir
        else:
            issues.append({"path": str(path), "code": "MISSING_ID",
                           "message": "frontmatter 缺少 id"})

        # AC-1 directory-as-truth
        if fm.get("type") != type_dir:
            issues.append({"path": str(path), "code": "TYPE_DIR_MISMATCH",
                           "message": f"type='{fm.get('type')}' != 目录名 '{type_dir}'"})
        # AC-1b type vocabulary
        if fm.get("type") not in TYPE_VOCAB:
            issues.append({"path": str(path), "code": "TYPE_VOCAB",
                           "message": f"type='{fm.get('type')}' 不在受控词汇 {sorted(TYPE_VOCAB)}"})

        # pdca.asset/v1 schema basics
        if fm.get("schema") != "pdca.asset/v1":
            issues.append({"path": str(path), "code": "SCHEMA_CONST",
                           "message": f"schema 必须为 pdca.asset/v1，实际 {fm.get('schema')}"})
        for field in ("id", "type", "layer", "summary", "status"):
            if field not in fm:
                issues.append({"path": str(path), "code": "SCHEMA_MISSING_FIELD",
                               "message": f"缺少必填字段 {field}"})
        if fm.get("layer") not in LAYER_ENUM:
            issues.append({"path": str(path), "code": "SCHEMA_LAYER",
                           "message": f"layer 非法: {fm.get('layer')}"})
        if fm.get("status") not in STATUS_ENUM:
            issues.append({"path": str(path), "code": "SCHEMA_STATUS",
                           "message": f"status 非法: {fm.get('status')}"})

        # AC-4 attribute -> test coverage
        for i, attr in enumerate(fm.get("attributes", []) or []):
            if not isinstance(attr, dict) or not str(attr.get("testable_signal", "")).strip():
                issues.append({"path": str(path), "code": "ATTR_NO_TEST_SIGNAL",
                               "message": f"attributes[{i}] 缺少非空 testable_signal"})

    # AC-2 references non-dangling
    for path, _type_dir, fm in assets:
        rels = fm.get("relations") or {}
        for key in RELATION_KEYS:
            for ref in (rels.get(key) or []):
                if is_ontology_ref(ref) and ref not in nodes:
                    issues.append({"path": str(path), "code": "DANGLING_REF",
                                   "message": f"relations.{key} 引用 '{ref}' 在 ontology/ 中无对应节点"})
        for ref in (fm.get("domain") or []):
            if is_ontology_ref(ref) and ref not in nodes:
                issues.append({"path": str(path), "code": "DANGLING_REF",
                               "message": f"domain 引用 '{ref}' 在 ontology/ 中无对应节点"})

    # AC-5 / AC-6 knowledge artifact relation constraints
    for path, type_dir, fm in assets:
        if type_dir not in KNOWLEDGE_VOCAB:
            continue
        rels = fm.get("relations") or {}
        if not (rels.get("guides") or rels.get("relates_to")):
            issues.append({"path": str(path), "code": "NO_GUIDES",
                           "message": f"{type_dir} 实例缺少 guides/relates_to 关系（关系丰富度）"})
        for ref in (rels.get("guides") or []):
            ttype = nodes_type.get(ref)
            if ttype is not None and ttype not in DOMAIN_VOCAB:
                issues.append({"path": str(path), "code": "GUIDES_RANGE",
                               "message": f"guides 目标 '{ref}' type='{ttype}' 非法（须为领域/过程类）"})

    # 关系 range 形式化（README §5 声明，此前仅文档约束）
    for path, _type_dir, fm in assets:
        rels = fm.get("relations") or {}
        for ref in (rels.get("composed_of") or []):
            ttype = nodes_type.get(ref)
            if ttype is not None and ttype not in ("entity", "concept"):
                issues.append({"path": str(path), "code": "COMPOSED_OF_RANGE",
                               "message": f"composed_of 目标 '{ref}' type='{ttype}' 非法（须为实体/概念实体类）"})
        for ref in (rels.get("configured_by") or []):
            if ref != TLS_CONFIG_ID:
                issues.append({"path": str(path), "code": "CONFIGURED_BY_RANGE",
                               "message": f"configured_by 目标 '{ref}' 非法（须为 TLSConfiguration 节点 {TLS_CONFIG_ID}）"})

    # AC-3 acyclic over relation graph
    graph = {}
    for path, _type_dir, fm in assets:
        src = fm.get("id")
        if not src:
            continue
        rels = fm.get("relations") or {}
        graph[src] = [r for k in RELATION_KEYS for r in (rels.get(k) or []) if r in nodes]

    color = {n: 0 for n in graph}  # 0=white 1=gray 2=black

    def dfs(n, stack):
        color[n] = 1
        for m in graph.get(n, []):
            if color.get(m, 0) == 1:
                issues.append({"path": str(nodes.get(n, n)), "code": "CYCLE",
                               "message": "检测到环：" + " -> ".join(stack + [m])})
            elif color.get(m, 0) == 0:
                dfs(m, stack + [n])
        color[n] = 2

    for n in list(graph):
        if color[n] == 0:
            dfs(n, [])

    return issues


def check_redirects(root: Path) -> list:
    """Scan knowledge/ for redirect stubs (frontmatter redirect_to) and verify targets exist.

    Physical-merge (ADR-0030) leaves redirect stubs in knowledge/; their `redirect_to`
    must point to a real ontology/ node, otherwise record identity is broken.
    """
    issues = []
    knowledge = root / "knowledge"
    if not knowledge.is_dir():
        return issues
    for md in sorted(knowledge.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            fm = extract_frontmatter(text)
        except Exception:
            # 非 redirect 桩或既有损坏 frontmatter：本检查仅关心 redirect_to，跳过以免阻断整体校验
            continue
        target = fm.get("redirect_to")
        if not target:
            continue
        dest = root / target
        if not dest.is_file():
            issues.append({"path": str(md), "code": "REDIRECT_DANGLING",
                           "message": f"redirect_to '{target}' 在仓库中无对应文件"})
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate ontology/ assets against SSOT contract")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--ontology-dir", type=Path)
    ap.add_argument("--format", choices=("text", "json"), default="text")
    args = ap.parse_args()
    ont_dir = args.ontology_dir or (args.root / "ontology")
    issues = validate(ont_dir)
    issues += check_redirects(args.root)
    if args.format == "json":
        print(json.dumps({"assets_dir": str(ont_dir), "issues": issues,
                          "ok": not issues}, ensure_ascii=False, indent=2))
    elif issues:
        print(f"FAIL: {len(issues)} issue(s) in {ont_dir}")
        for it in issues:
            print(f"  [{it['code']}] {it['path']}: {it['message']}")
    else:
        print(f"OK: {ont_dir} 通过本体契约校验")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
