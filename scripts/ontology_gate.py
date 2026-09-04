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
        reason = str(meta.get("ontology_exempt_reason") or "")
        if len(reason) < 20 or "ontology" not in reason.lower():
            return [Issue("ONTOLOGY_EXEMPT_REASON_MISSING", "task.json",
                          f"ontology_exempt=true 时须提供 ontology_exempt_reason ≥20字符且含ontology关键词，实际: '{reason[:30]}'",
                          "在 task.json meta 写入 ontology_exempt_reason: 'ontology自举：xxx（关联 ontology:concept/ontology-creation-gate）'")]
        return []
    frag = meta.get("ontology_fragment")
    if not frag:
        scen = meta.get("scenario_type", "unknown")
        return [Issue("ONTOLOGY_FRAGMENT_MISSING", "task.json",
                      f"do 前置 ontology-ready：meta.ontology_fragment 未设置（scenario_type={scen}）；"
                      f"请声明 ontology_fragment 或设 ontology_exempt=true 并说明豁免原因",
                      "设置 meta.ontology_fragment 指向 ontology 片段，或在 task.json 设 ontology_exempt=true")]
    frag_path = Path(frag) if Path(frag).is_absolute() else (root / frag)
    if not frag_path.exists():
        return [Issue("ONTOLOGY_FRAGMENT_DANGLING", "task.json",
                      f"meta.ontology_fragment 指向不存在路径: {frag}")]
    bad = []
    for md in sorted(frag_path.rglob("*.md")):
        if md.name == "README.md" or md.name == "FROZEN.md":
            continue
        # 跳过 FAIR 的非本体桶（versions/competency_questions 等）
        if any(part in ("versions", "competency_questions", "provenance", "documentation") for part in md.parts):
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
        # 允许 domain 的物理子目录分域（domain/pdca 等），type 仍为 domain
        expected_type = md.parent.name
        # 若父目录为 domain 的子域（pdca/zfs 等），期望 type 仍为 domain
        if md.parent.parent.name == "domain" and md.parent.name in ("pdca", "zfs", "bcachefs", "report-center", "core"):
            expected_type = "domain"
        if fm.get("type") != expected_type:
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


# ---------- 新增：evidence→ontology 自动反哺 ----------
LEGACY_SUPPORT_KINDS = {
    "document", "documentation", "concept", "entity", "process", "role",
    "pattern", "principle", "pitfall", "fact", "decision", "knowledge",
    "test", "script", "adr", "skill", "validation-report", "redirect",
}


def auto_induce_evidence(task: dict, root: Path) -> list:
    """Act 阶段 evidence→ontology 自动反哺检查（顾问式，不阻断）。

    扫描 records/<record>/evidence/manifest.jsonl：
    - 统计 evidence 条目中 kind 属于 LEGACY_SUPPORT_KINDS 但未锚定到
      pdca-evidence 子类型的条目（说明该领域知识尚未本体化）；
    - 若存在此类条目，返回一条 AUTO_INDUCE_CANDIDATE 提示，建议运行
      `python3 scripts/ontology_induction.py --adapter evidence --source records/<record>/evidence/manifest.jsonl`。
    顾问式：不阻断 Act，仅提供可执行指引；无证据或已全部锚定时返回 []。
    """
    phase = (task.get("meta") or {}).get("phase")
    if phase not in ("act", "archive"):
        return []
    record = (task.get("meta") or {}).get("record")
    if not record:
        return []
    manifest = root / "records" / str(record) / "evidence" / "manifest.jsonl"
    if not manifest.is_file():
        return []
    try:
        import json as _json
        candidates = []
        for line in manifest.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = _json.loads(line)
            except Exception:
                continue
            if entry.get("superseded_by"):
                continue
            kind = str(entry.get("kind", ""))
            ref = entry.get("evidence_type_ref")
            # LEGACY_SUPPORT_KINDS 且未锚定 -> 潜在本体缺口
            if kind in LEGACY_SUPPORT_KINDS and not ref:
                # 进一步：仅当 kind 对应知识形态时提示（如 pattern/principle/pitfall/fact/decision）
                if kind in {"pattern", "principle", "pitfall", "fact", "decision", "concept", "entity", "process"}:
                    candidates.append(entry.get("id", kind))
        if candidates:
            return [Issue(
                "AUTO_INDUCE_CANDIDATE",
                str(manifest.relative_to(root)) if manifest.is_relative_to(root) else str(manifest),
                f"检测到 {len(candidates)} 条未锚定 evidence（{', '.join(candidates[:3])}）可反哺本体；"
                f"建议运行: python3 scripts/ontology_induction.py --adapter evidence --source {manifest}",
                f"python3 scripts/ontology_induction.py --adapter evidence --source {manifest} --out print",
            )]
    except Exception:
        pass
    return []


def auto_induce_flow_issues(root: Path, threshold: int = 3) -> list:
    """FlowIssue → 本体补强自动触发（顾问式）。

    读取聚合后的 flow-issue backlog（pdca/improvements/flow-issue-backlog.json），
    若某 issue 的 occurrence_count >= threshold 且尚未创建 improvement candidate，
    则提示可自动创建候选。返回 Issue 列表（不阻断，仅提示）。
    阈值可配置，默认 3 次 occurrence 触发。
    """
    backlog_path = root / "pdca" / "improvements" / "flow-issue-backlog.json"
    if not backlog_path.is_file():
        return []
    try:
        import json as _json
        data = _json.loads(backlog_path.read_text(encoding="utf-8"))
        issues = data.get("issues") or data.get("items") or []
        if isinstance(data, list):
            issues = data
        cands: list[Issue] = []
        for item in issues:
            cnt = item.get("occurrence_count") or item.get("count") or len(item.get("occurrences") or [])
            fid = item.get("id") or item.get("fingerprint") or "unknown"
            has_candidate = bool(item.get("candidate_id") or item.get("improvement_candidate"))
            if isinstance(cnt, int) and cnt >= threshold and not has_candidate:
                cands.append(Issue(
                    "AUTO_FLOW_INDUCE_CANDIDATE",
                    str(backlog_path.relative_to(root)) if backlog_path.is_relative_to(root) else str(backlog_path),
                    f"FlowIssue {fid} occurrence_count={cnt} >= {threshold}，建议自动创建本体补强 candidate",
                    f"python3 scripts/create-improvement-candidate.py --issue {fid} --threshold {threshold}",
                ))
                # 仅提示前 3 条，避免刷屏
                if len(cands) >= 3:
                    break
        return cands
    except Exception:
        return []
