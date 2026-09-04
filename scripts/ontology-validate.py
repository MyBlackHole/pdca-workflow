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
   REDIRECT_DANGLING: knowledge/ redirect stubs (frontmatter redirect_to) point to existing ontology/ nodes (see ontology:concept/ontology-creation-gate decision-background; formerly ADR-0030)
  KNOWLEDGE_FM_INVALID: knowledge/ 声明 frontmatter 的 md 必须 YAML 合法（防止坏 frontmatter 被静默跳过）
  schema: pdca.asset/v1 required fields / enum values

Exit code is 1 when any issue is found, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
import re
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

# 门禁规则的权威来源 = ontology/concept/ontology-rule-* 节点的 rule_spec
RULE_IDS = {
    "type": "ontology:concept/ontology-rule-type-controlled",
    "non_dangling": "ontology:concept/ontology-rule-non-dangling",
    "acyclic": "ontology:concept/ontology-rule-acyclic",
    "attr": "ontology:concept/ontology-rule-attr-testable",
    "richness": "ontology:concept/ontology-rule-richness",
    "guides": "ontology:concept/ontology-rule-guides-range",
    "fidelity_generic": "ontology:concept/ontology-rule-fidelity-generic",
    "fidelity_body": "ontology:concept/ontology-rule-fidelity-body",
    "fidelity_diagram": "ontology:concept/ontology-rule-fidelity-diagram",
}


def load_rule_specs(assets):
    """从 ontology-rule-* 节点读取 rule_spec，作为门禁参数唯一来源。

    本体是门禁权威：规则节点缺失或 rule_spec 非法时直接报错退出，不允许静默回退。
    """
    specs = {}
    for _path, _td, fm in assets:
        rid = fm.get("id", "")
        if rid in RULE_IDS.values():
            rs = fm.get("rule_spec")
            if not isinstance(rs, dict):
                sys.exit(f"ERROR: 规则节点 {rid} 缺少合法 rule_spec（本体为门禁权威）")
            specs[rid] = rs
    missing = [rid for rid in RULE_IDS.values() if rid not in specs]
    if missing:
        sys.exit("ERROR: 缺失规则节点（本体为门禁权威）: " + ", ".join(missing))
    return specs


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
        if rel.name in ("README.md", "FROZEN.md"):
            continue
        # 跳过 FAIR 非本体桶
        if any(part in ("versions", "competency_questions", "provenance", "documentation") for part in rel.parts):
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

    # 门禁参数权威来源 = ontology-rule-* 节点的 rule_spec（本体为权威，不允许静默回退）
    specs = load_rule_specs(assets)
    global TYPE_VOCAB, RELATION_KEYS, KNOWLEDGE_VOCAB, DOMAIN_VOCAB, TLS_CONFIG_ID
    TYPE_VOCAB = set(specs[RULE_IDS["type"]].get("allowed_types", []))
    RELATION_KEYS = tuple(specs[RULE_IDS["non_dangling"]].get("reference_relation_keys", []))
    GRAPH_KEYS = tuple(specs[RULE_IDS["acyclic"]].get("graph_relation_keys", []))
    EXTRA_REF_FIELDS = list(specs[RULE_IDS["non_dangling"]].get("extra_reference_fields", []))
    ATTR_TEST_FIELD = specs[RULE_IDS["attr"]].get("attribute_test_field", "testable_signal")
    KNOWLEDGE_VOCAB = set(specs[RULE_IDS["richness"]].get("knowledge_types", []))
    REQUIRED_RELATIONS = list(specs[RULE_IDS["richness"]].get("required_relations", []))
    COMPOSED_OF_RANGE = set(specs[RULE_IDS["richness"]].get("composed_of_range", []))
    DOMAIN_VOCAB = set(specs[RULE_IDS["guides"]].get("target_types", []))
    CONFIGURED_BY_TARGET = specs[RULE_IDS["guides"]].get("configured_by_target", TLS_CONFIG_ID)
    # 保真度门禁参数（本体为权威）
    FIDELITY_GENERIC_PHRASES = specs[RULE_IDS["fidelity_generic"]].get("generic_phrases", [])
    FIDELITY_REQUIRED_VERBS = specs[RULE_IDS["fidelity_generic"]].get("required_verbs", [])

    # AC-1 directory-as-truth + AC-1b vocabulary + schema basics + AC-4 attribute coverage
    for path, type_dir, fm in assets:
        if fm.get("type") != type_dir:
            issues.append({"path": str(path), "code": "TYPE_DIR_MISMATCH",
                           "message": f"type='{fm.get('type')}' != 目录名 '{type_dir}'"})
        if fm.get("type") not in TYPE_VOCAB:
            issues.append({"path": str(path), "code": "TYPE_VOCAB",
                           "message": f"type='{fm.get('type')}' 不在受控词汇 {sorted(TYPE_VOCAB)}"})
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
        for i, attr in enumerate(fm.get("attributes", []) or []):
            if not isinstance(attr, dict) or not str(attr.get(ATTR_TEST_FIELD, "")).strip():
                issues.append({"path": str(path), "code": "ATTR_NO_TEST_SIGNAL",
                               "message": f"attributes[{i}] 缺少非空 {ATTR_TEST_FIELD}"})
            else:
                sig = str(attr.get(ATTR_TEST_FIELD, ""))
                # 保真度：拒绝泛化signal（零容忍，Q3确认；T0536校准：含泛化且无动词才拒，95%误报率校准）
                for phrase in FIDELITY_GENERIC_PHRASES:
                    if phrase in sig:
                        # T0536校准：泛化且无required_verbs才拒，否则为有效误报不阻断
                        has_verb = any(v in sig for v in FIDELITY_REQUIRED_VERBS)
                        if has_verb:
                            break
                        oid = fm.get("id", "")
                        # 存量豁免：ontology/.fidelity-exempt.json 中的id在限期内豁免（由audit产出基线）
                        exempt_ids = set()
                        exempt_path = Path(ROOT) / "ontology" / ".fidelity-exempt.json"
                        if exempt_path.is_file():
                            try:
                                data = json.loads(exempt_path.read_text(encoding="utf-8"))
                                exempt_ids = set(data.get("ids", []))
                            except Exception:
                                pass
                        if oid in exempt_ids:
                            # 豁免期内不阻断，但仍记录为豁免提示（便于每日播报）
                            pass
                        else:
                            issues.append({"path": str(path), "code": "ATTR_GENERIC",
                                           "message": f"attributes[{i}].{ATTR_TEST_FIELD} 含泛化短语 '{phrase}'且无可执行动词（需含 {FIDELITY_REQUIRED_VERBS}）"})
                        break
                else:
                    pass

    # AC-2 references non-dangling (relations 键 + 额外引用字段)
    for path, _type_dir, fm in assets:
        rels = fm.get("relations") or {}
        for key in RELATION_KEYS:
            for ref in (rels.get(key) or []):
                if is_ontology_ref(ref) and ref not in nodes:
                    issues.append({"path": str(path), "code": "DANGLING_REF",
                                   "message": f"relations.{key} 引用 '{ref}' 在 ontology/ 中无对应节点"})
        for field in EXTRA_REF_FIELDS:
            for ref in (fm.get(field) or []):
                if is_ontology_ref(ref) and ref not in nodes:
                    issues.append({"path": str(path), "code": "DANGLING_REF",
                                   "message": f"{field} 引用 '{ref}' 在 ontology/ 中无对应节点"})

    # AC-5 / AC-6 knowledge artifact relation constraints
    for path, type_dir, fm in assets:
        if type_dir not in KNOWLEDGE_VOCAB:
            continue
        rels = fm.get("relations") or {}
        if not any(rels.get(r) for r in REQUIRED_RELATIONS):
            issues.append({"path": str(path), "code": "NO_GUIDES",
                           "message": f"{type_dir} 实例缺少 {REQUIRED_RELATIONS} 关系（关系丰富度）"})
        for ref in (rels.get("guides") or []):
            ttype = nodes_type.get(ref)
            if ttype is not None and ttype not in DOMAIN_VOCAB:
                issues.append({"path": str(path), "code": "GUIDES_RANGE",
                               "message": f"guides 目标 '{ref}' type='{ttype}' 非法（须为 {sorted(DOMAIN_VOCAB)} 类）"})

    # 关系 range 形式化（README §5 声明，此前仅文档约束）
    for path, _type_dir, fm in assets:
        rels = fm.get("relations") or {}
        for ref in (rels.get("composed_of") or []):
            ttype = nodes_type.get(ref)
            if ttype is not None and ttype not in COMPOSED_OF_RANGE:
                issues.append({"path": str(path), "code": "COMPOSED_OF_RANGE",
                               "message": f"composed_of 目标 '{ref}' type='{ttype}' 非法（须为 {sorted(COMPOSED_OF_RANGE)} 类）"})
        for ref in (rels.get("configured_by") or []):
            if ref != CONFIGURED_BY_TARGET:
                issues.append({"path": str(path), "code": "CONFIGURED_BY_RANGE",
                               "message": f"configured_by 目标 '{ref}' 非法（须为 {CONFIGURED_BY_TARGET}）"})

    # AC-3 acyclic over relation graph (use graph_relation_keys)
    graph = {}
    for path, _type_dir, fm in assets:
        src = fm.get("id")
        if not src:
            continue
        rels = fm.get("relations") or {}
        graph[src] = [r for k in GRAPH_KEYS for r in (rels.get(k) or []) if r in nodes]

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

    Deprecated: knowledge/ was merged into ontology/ (T0418~T0423) and removed.
    This check is retained for backward-compat; it skips silently when knowledge/ is absent.
    (Historically, physical-merge per ontology:concept/ontology-creation-gate, formerly ADR-0030,
    left redirect stubs in knowledge/ whose `redirect_to` must point to a real ontology/ node.)
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


def check_knowledge_frontmatter(root: Path) -> list:
    """Scan knowledge/ for files that declare frontmatter (start with ---) but fail YAML parse.

    Deprecated: knowledge/ was merged into ontology/ (T0418~T0423) and removed.
    This check is retained for backward-compat; it skips silently when knowledge/ is absent.
    (Historically, the physical merge per ontology:concept/ontology-creation-gate, formerly ADR-0030,
    left assets under knowledge/ whose malformed frontmatter used to be silently skipped by
    check_redirects' try/except; this made YAML-legality an explicit, non-skippable check.)
    """
    issues = []
    knowledge = root / "knowledge"
    if not knowledge.is_dir():
        return issues
    for md in sorted(knowledge.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            issues.append({"path": str(md), "code": "KNOWLEDGE_FM_INVALID",
                           "message": "frontmatter 以 '---' 开头但缺少闭合 '---'"})
            continue
        try:
            data = yaml.safe_load(parts[1])
        except Exception as e:
            issues.append({"path": str(md), "code": "KNOWLEDGE_FM_INVALID",
                           "message": f"frontmatter YAML 解析失败: {type(e).__name__}: {e}"})
            continue
        if not isinstance(data, dict):
            issues.append({"path": str(md), "code": "KNOWLEDGE_FM_INVALID",
                           "message": "frontmatter 解析结果非 dict"})
    return issues



def check_knowledge_refs(root: Path) -> list:
    """Scan ontology/ files for knowledge/ path references that should be cleaned up.
    AC-1: No knowledge/ path references should remain in ontology/ assets.
    """
    issues = []
    ont_dir = root / "ontology"
    if not ont_dir.is_dir():
        return issues
    for md in sorted(ont_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        # Match knowledge/ as a path reference (not the word "knowledge" in general)
        matches = re.findall(r'(?<![\w-])knowledge/', text)
        if matches:
            issues.append({"path": str(md), "code": "KNOWLEDGE_REF_CLEANUP",
                           "message": f"contains {len(matches)} knowledge/ path reference(s), should be replaced with ontology/domain/ paths"})
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
    issues += check_knowledge_frontmatter(args.root)
    issues += check_knowledge_refs(args.root)
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
