"""ontology-ready 门禁：do 阶段准入校验任务领域本体片段。

由 PDCA 元本体 pdca-gate / pdca-ontology-ready 驱动：仅当某阶段准入条件
含 ontology-ready 时才校验；自举任务（meta.ontology_exempt）豁免。
另含结论锚定（verdict -> pdca-verdict 子类型）与归档本体自检，补全全流程闭环。
"""
from __future__ import annotations

import re
import subprocess
import sys
import yaml
from pathlib import Path

from pdca_core import Issue

import ontology_reason

ROOT = Path(__file__).resolve().parent.parent
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


def verdict_anchor_issues(task: dict, root: Path) -> list:
    """结论锚定：meta.verdict.outcome 必须映射到已存在的 pdca-verdict 子类型节点。

    仅在任务已产生 verdict（phase ∈ check/act/archive）时校验；无 verdict 时不阻断。
    """
    phase = (task.get("meta") or {}).get("phase")
    if phase not in ("check", "act", "archive"):
        return []
    verdict = (task.get("meta") or {}).get("verdict")
    if not verdict:
        return []
    outcome = verdict.get("outcome")
    if outcome not in ("confirmed", "rejected", "partial"):
        return []
    ont = root / "ontology"
    nodes = ontology_reason.load_ontology(ont) if ont.is_dir() else {}
    nid = f"ontology:entity/verdict-{outcome}"
    if nid not in nodes:
        return [Issue("VERDICT_ANCHOR_MISSING", "task.json",
                      f"结论 outcome='{outcome}' 无对应本体节点 {nid}（pdca-verdict 子类型缺失）")]
    return []


def archive_ontology_ready_issues(root: Path) -> list:
    """归档本体自检：ontology-validate 通过且无孤岛，否则拒绝归档。"""
    ont = root / "ontology"
    if not ont.is_dir():
        return []
    issues = []
    val = subprocess.run(
        [sys.executable, str(root / "scripts" / "ontology-validate.py"), "--ontology-dir", str(ont)],
        capture_output=True, text=True,
    )
    if val.returncode != 0:
        last = val.stdout.strip().splitlines()[-1] if val.stdout.strip() else "ontology-validate 失败"
        issues.append(Issue("ARCHIVE_ONTOLOGY_INVALID", "ontology", last))
    try:
        g = subprocess.run(
            [sys.executable, str(root / "scripts" / "ontology_graph.py"), "--root", str(ont), "--format", "summary"],
            capture_output=True, text=True,
        )
        m = re.search(r"islands:\s*(\d+)", g.stdout)
        if m and int(m.group(1)) != 0:
            issues.append(Issue("ARCHIVE_ONTOLOGY_ISLANDS", "ontology",
                                f"存在 {m.group(1)} 个孤岛节点，归档前须消除"))
    except Exception:
        pass
    return issues
