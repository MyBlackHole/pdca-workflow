"""ontology-ready 门禁：do 阶段准入校验任务领域本体片段。

由 PDCA 元本体 pdca-gate / pdca-ontology-ready 驱动：仅当某阶段准入条件
含 ontology-ready 时才校验；自举任务（meta.ontology_exempt）豁免。
"""
from __future__ import annotations

import yaml
from pathlib import Path

from pdca_core import Issue

import ontology_reason

REQUIRED_FM = ("schema", "id", "type", "layer", "summary", "status")


def ontology_ready_issues(task: dict, root: Path) -> list:
    phase = (task.get("meta") or {}).get("phase")
    if phase is None:
        return []
    if "ontology-ready" not in ontology_reason.admission_conditions(phase, ont_dir=root / "ontology"):
        return []
    meta = task.get("meta") or {}
    if meta.get("ontology_exempt"):
        return []
    frag = meta.get("ontology_fragment")
    if not frag:
        return [Issue("ONTOLOGY_FRAGMENT_MISSING", "task.json",
                      "do 前置 ontology-ready：meta.ontology_fragment 未设置")]
    frag_path = Path(frag) if Path(frag).is_absolute() else (root / frag)
    if not frag_path.exists():
        return [Issue("ONTOLOGY_FRAGMENT_DANGLING", "task.json",
                      f"meta.ontology_fragment 指向不存在路径: {frag}")]
    bad = []
    for md in sorted(frag_path.rglob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            bad.append(f"{md.name}: 缺少 frontmatter")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            bad.append(f"{md.name}: frontmatter 未闭合")
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception as e:
            bad.append(f"{md.name}: YAML 错误 {e}")
            continue
        if not isinstance(fm, dict):
            bad.append(f"{md.name}: frontmatter 非 dict")
            continue
        for f in REQUIRED_FM:
            if f not in fm:
                bad.append(f"{md.name}: 缺字段 {f}")
        if fm.get("schema") != "pdca.asset/v1":
            bad.append(f"{md.name}: schema 非法")
        if fm.get("type") != md.parent.name:
            bad.append(f"{md.name}: type!=目录名")
    if bad:
        return [Issue("ONTOLOGY_FRAGMENT_INVALID", "task.json", "; ".join(bad[:5]))]
    return []
