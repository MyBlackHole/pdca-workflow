#!/usr/bin/env python3
"""PDCA 元本体推理层。

读取 ontology/ 中的 pdca-* 元本体节点，回答：
  - 某 phase->phase 转换是否合法（依据 pdca-transition 的 composed_of）
  - 某阶段准入条件（依据 pdca-gate / pdca-ontology-ready）
  - 某 evidence 类型是否被 PDCA 元本体识别（evidence->AC 满足判定的类型层）

元本体缺失时回退到硬编码最小核心（plan/do/check/act/archive），
保证自举期 transition 不死锁。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RELATION_KEYS = (
    "specializes", "instance_of", "composed_of", "configured_by",
    "part_of", "guides", "relates_to",
)
PDCA_ROOT_ID = "ontology:concept/pdca"

FALLBACK_PHASES = ["plan", "do", "check", "act", "archive"]
FALLBACK_LEGAL = {
    ("plan", "do"), ("do", "check"), ("check", "act"), ("act", "archive"),
}
FALLBACK_ADMISSION = {"do": ["ontology-ready"]}
FALLBACK_EVIDENCE = {"test-result", "convergence-map", "review"}


def _fm(path: Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else {}


def load_ontology(ont_dir: Path) -> dict:
    nodes: dict = {}
    if not ont_dir.is_dir():
        return nodes
    for md in sorted(ont_dir.rglob("*.md")):
        if md.name == "README.md":
            continue
        fm = _fm(md)
        oid = fm.get("id")
        if oid:
            nodes[oid] = fm
    return nodes


def has_meta(nodes: dict) -> bool:
    return PDCA_ROOT_ID in nodes


def _phase_ids(nodes: dict) -> list[str]:
    out = []
    for oid, fm in nodes.items():
        if fm.get("type") != "entity":
            continue
        spec = fm.get("relations", {}).get("specializes") or []
        if spec == ["ontology:concept/pdca-phase"]:
            out.append(oid.split("/")[-1].replace("phase-", ""))
    return out


def legal_transition(src: str, dst: str, nodes: dict | None = None, ont_dir: Path | None = None) -> bool:
    if nodes is None:
        nodes = load_ontology(ont_dir or ROOT / "ontology")
    if not has_meta(nodes):
        return (src, dst) in FALLBACK_LEGAL
    src_id = f"ontology:entity/phase-{src}"
    dst_id = f"ontology:entity/phase-{dst}"
    for fm in nodes.values():
        if fm.get("type") != "entity":
            continue
        rels = fm.get("relations") or {}
        spec = rels.get("specializes") or []
        if "ontology:concept/pdca-transition" not in spec:
            continue
        co = rels.get("composed_of") or []
        if len(co) == 2 and co[0] == src_id and co[1] == dst_id:
            return True
    return False


def transition_targets(src: str, nodes: dict | None = None, ont_dir: Path | None = None) -> list[str]:
    if nodes is None:
        nodes = load_ontology(ont_dir or ROOT / "ontology")
    phases = _phase_ids(nodes) if has_meta(nodes) else list(FALLBACK_PHASES)
    return [dst for dst in phases if legal_transition(src, dst, nodes)]


def admission_conditions(phase: str, nodes: dict | None = None, ont_dir: Path | None = None) -> list[str]:
    if nodes is None:
        nodes = load_ontology(ont_dir or ROOT / "ontology")
    if not has_meta(nodes):
        return list(FALLBACK_ADMISSION.get(phase, []))
    gid = f"ontology:concept/pdca-gate-{phase}"
    gfm = nodes.get(gid)
    if not gfm:
        return []
    rels = gfm.get("relations") or {}
    conds = []
    for ref in (rels.get("relates_to") or []):
        if ref == f"ontology:entity/phase-{phase}":
            continue
        slug = ref.split("/")[-1]
        if slug.startswith("pdca-"):
            slug = slug[len("pdca-"):]
        conds.append(slug)
    return conds


def recognized_evidence(evidence_type: str, nodes: dict | None = None, ont_dir: Path | None = None) -> bool:
    if nodes is None:
        nodes = load_ontology(ont_dir or ROOT / "ontology")
    if not has_meta(nodes):
        return evidence_type in FALLBACK_EVIDENCE
    eid = f"ontology:entity/evidence-{evidence_type}"
    if eid not in nodes:
        return False
    spec = nodes[eid].get("relations", {}).get("specializes") or []
    return spec == ["ontology:concept/pdca-evidence"]


def evidence_satisfies_ac(evidence_type: str, ac: str, nodes: dict | None = None, ont_dir: Path | None = None) -> bool:
    return recognized_evidence(evidence_type, nodes, ont_dir)


def main() -> int:
    ap = argparse.ArgumentParser(description="PDCA 元本体推理层")
    ap.add_argument("query", choices=["legal-transition", "admission", "recognized-evidence"])
    ap.add_argument("--from", dest="src")
    ap.add_argument("--to", dest="dst")
    ap.add_argument("--phase")
    ap.add_argument("--evidence")
    ap.add_argument("--ontology-dir", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    ont = args.ontology_dir or (ROOT / "ontology")
    if args.query == "legal-transition":
        result = legal_transition(args.src, args.dst, ont_dir=ont)
    elif args.query == "admission":
        result = admission_conditions(args.phase, ont_dir=ont)
    else:
        result = recognized_evidence(args.evidence, ont_dir=ont)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
