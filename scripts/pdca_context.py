#!/usr/bin/env python3
"""PDCA 阶段上下文：实时读取 PDCA 元本体并按 phase 输出执行指引。

直接消费 PDCA 元本体知识（pdca-* 节点正文 + ontology_reason 推理结果），
供执行层（transition-phase / flow-plan|do|check|act）在每个阶段入口拉取：
  - 阶段定义（来自 phase-<phase>.md 正文）
  - 准入条件（ontology_reason.admission_conditions）
  - 合法后继（ontology_reason.transition_targets）
  - 关联概念知识（pdca-gate-<phase>.relates_to 指向的节点正文，如门禁理由/verdict 含义）

元本体缺失时回退到硬编码最小提示，绝不抛异常中断流程。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

import ontology_reason as ore

ROOT = Path(__file__).resolve().parent.parent
PHASES = ["plan", "do", "check", "act", "archive"]

FALLBACK_DEF = {
    "plan": "Plan：澄清目标与范围，写 PRD 与验收标准。",
    "do": "Do：按 PRD 实现并登记证据。",
    "check": "Check：对照 PRD 与证据验证假设，封存 verdict。",
    "act": "Act：沉淀知识、处置并归档。",
    "archive": "Archive：将任务移出活跃区，保留不可变记录。",
}


def _body(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return text.strip()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    return parts[2].strip()


def load_bodies(ont_dir: Path) -> dict:
    bodies: dict = {}
    if not ont_dir.is_dir():
        return bodies
    for md in sorted(ont_dir.rglob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        oid = fm.get("id") if isinstance(fm, dict) else None
        if oid:
            bodies[oid] = parts[2].strip()
    return bodies


def render(phase: str, ont_dir: Path, as_json: bool = False) -> str:
    nodes = ore.load_ontology(ont_dir)
    bodies = load_bodies(ont_dir)
    has_meta = ore.has_meta(nodes)

    definition = bodies.get(f"ontology:entity/phase-{phase}", "")
    conds = ore.admission_conditions(phase, nodes=nodes)
    targets = ore.transition_targets(phase, nodes=nodes)

    related = []
    gid = f"ontology:concept/pdca-gate-{phase}"
    if gid in nodes:
        for ref in (nodes[gid].get("relations", {}).get("relates_to") or []):
            if ref == f"ontology:entity/phase-{phase}":
                continue
            body = bodies.get(ref)
            if body:
                related.append((ref, body))

    if as_json:
        return json.dumps(
            {
                "phase": phase,
                "has_meta": has_meta,
                "definition": definition,
                "admission": conds,
                "next_transitions": targets,
                "related_concepts": [r[0] for r in related],
            },
            ensure_ascii=False,
            indent=2,
        )

    if not has_meta:
        lines = [
            f"# PDCA 阶段指引：{phase}",
            "",
            FALLBACK_DEF.get(phase, ""),
            "",
            "（注：PDCA 元本体缺失，使用硬编码回退提示；元本体恢复后将以节点知识为准。）",
        ]
        return "\n".join(lines)

    lines = [f"# PDCA 阶段指引：{phase}", ""]
    if definition:
        lines += ["## 阶段定义", definition, ""]
    lines += ["## 准入条件"]
    lines += [f"- {c}" for c in conds] or ["- (无)"]
    lines += ["", "## 合法后继", ", ".join(targets) if targets else "(无)", ""]
    for ref, body in related:
        lines += [f"## 关联概念：{ref}", body, ""]
    return "\n".join(lines).rstrip()


def main() -> int:
    ap = argparse.ArgumentParser(description="PDCA 阶段上下文（实时消费元本体知识）")
    ap.add_argument("--phase", required=True, choices=PHASES)
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        out = render(args.phase, args.ontology_dir, as_json=args.json)
    except Exception as exc:  # 绝不中断调用方（如 transition-phase）
        out = f"# PDCA 阶段指引：{args.phase}\n\n(元本体读取失败，回退提示：{exc})"
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
