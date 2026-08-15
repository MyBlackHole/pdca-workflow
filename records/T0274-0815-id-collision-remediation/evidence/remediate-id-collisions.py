#!/usr/bin/env python3
"""ID 撞车全链路重分配器（T0274）。

为历史遗留的重复 task_id 撞车组执行全链路重分配：
- 重分配方 task.json 改写 id/meta.record
- records 目录重命名
- 归档目录重命名
- 全库 parent/children/dependencies 引用链替换旧 ID

幂等：重复运行不产生二次改写。执行前必须先 dry-run 预览。

用法：
  remediate-id-collisions.py --dry-run [--json]   # 预览（不改动）
  remediate-id-collisions.py --check-cover        # 校验裁决表覆盖 doctor 全量
  remediate-id-collisions.py --check-disposable   # 校验可处置组全归档
  remediate-id-collisions.py --check-deferred     # 校验待办组含活跃任务
  remediate-id-collisions.py --apply              # 实际执行重分配
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_ROOT = ROOT / "pdca" / "tasks"
RECORDS_ROOT = ROOT / "records"

# 12 组可处置重分配：旧 task_id -> (重分配方目录相对片段, 新 task_id)
# 主流方（保留原 ID）不在此表；11 组活跃待办组由 check-deferred 验证。
# 撞车组同 ID 无法字符串区分引用归属。REFERENCE_CONTEXT 提供"上下文判定"：
#   对声明 parent/children/dependencies=旧ID 的任务，按 (旧ID, 被引用方任务 slug)
#   判定该引用指向保留方还是重分配方。
#   slug 含关键片段 → 属于重分配方（引用须改新 ID）；否则视为保留方（不改）。
REASSIGNMENTS: dict[str, tuple[str, str]] = {
    "T0142": ("0729-vmcore-analysis", "T0275"),
    "T0163": ("0731-nbu-dte-enforced-mechanism", "T0276"),
    "T0214": ("0804-cdm-report-center-analyse", "T0277"),
    "T0215": ("0804-report-subscheme-docs", "T0278"),
    "T0217": ("0804-cdm-data-cli", "T0279"),
    "T0224": ("0808-bwlimit-poc", "T0280"),
    "T0225": ("0807-xtrabackup-incremental-tech", "T0281"),
    "T0244": ("0812-rpc-metadata-analysis", "T0282"),
    "T0246": ("0810-backup-gm-transport-encryption", "T0283"),
    "T0247": ("0811-backup-doc-optimize", "T0284"),
    "T0249": ("0812-kernel-nfs-gm-research", "T0285"),
    "T0251": ("0814-oss-xmake-integration", "T0286"),
}

# 11 组含活跃任务的撞车：整组跳过，任何任务（含其归档侧）都不改写。
DEFERRED_IDS: set[str] = {
    "T0216", "T0218", "T0219", "T0220", "T0221", "T0222",
    "T0228", "T0229", "T0248", "T0250", "T0252",
}

# 需上下文判定引用归属的撞车组（存在 CDM/报表树 与 RPC 树 纠缠）：
#   CDM/报表链特征词（slug 含任一）→ 引用指向重分配方，改新 ID；
#   RPC 链特征词 → 引用指向保留方，保持旧 ID。
CONTEXTUAL_GROUPS: set[str] = {"T0214", "T0215", "T0217"}
CDM_FEATURES: tuple[str, ...] = ("report", "cdm", "collection", "deployment", "acceptance")
RPC_FEATURES: tuple[str, ...] = ("rpc", "worker", "epoll")


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _doctor_duplicates() -> list[dict]:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "pdca-doctor.py"), "--json"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    d = json.loads(r.stdout)
    return d["identity"]["duplicate_task_ids"]


def _find_task_dirs(fragment: str) -> list[Path]:
    """按目录名后缀片段定位任务目录（含 task.json）。

    片段为纯 slug（如 0804-report-subscheme-docs），匹配 `Txxxx-<slug>`
    或 `<slug>` 两种命名；重命名后再次运行仍可定位（幂等）。
    """
    hits = []
    for candidate in TASKS_ROOT.glob(f"**/*{fragment}"):
        if (candidate / "task.json").is_file():
            hits.append(candidate)
    return hits


def _record_rename(task_id: str, slug: str) -> str:
    return f"{task_id}-{slug}"


def build_plan() -> list[dict]:
    """构建重分配计划。"""
    plan = []
    for old_id, (dir_frag, new_id) in REASSIGNMENTS.items():
        dirs = _find_task_dirs(dir_frag)
        if len(dirs) != 1:
            raise RuntimeError(f"{old_id}: 重分配目录 {dir_frag} 匹配 {len(dirs)} 个，期望 1")
        task_dir = dirs[0]
        task_path = task_dir / "task.json"
        task = _load_json(task_path)
        slug = task.get("slug")
        old_record = task.get("meta", {}).get("record")
        new_record = _record_rename(new_id, slug) if slug else None
        plan.append({
            "old_id": old_id,
            "new_id": new_id,
            "slug": slug,
            "task_dir": str(task_dir.relative_to(ROOT)),
            "old_record": old_record,
            "new_record": new_record,
        })
    return plan


def check_cover() -> dict:
    dups = _doctor_duplicates()
    doctor_ids = {g["task_id"] for g in dups}
    reassigned_ids = set(REASSIGNMENTS.keys())
    # 每组的重分配方目录必须在 doctor 报告路径中（目录名 `<slug>` 或 `<Txxxx>-<slug>` 均可）
    uncovered = []
    for old_id, (dir_frag, _) in REASSIGNMENTS.items():
        hit = any(p.split("/")[-2].endswith(dir_frag)
                  for g in dups if g["task_id"] == old_id for p in g["paths"])
        if not hit:
            uncovered.append(old_id)
    return {
        "doctor_groups": len(dups),
        "covered": len(doctor_ids & reassigned_ids),
        "deferred": len(doctor_ids - reassigned_ids),
        "reassigning": len(REASSIGNMENTS),
        "uncovered": uncovered,
    }


def check_disposable() -> dict:
    """可处置组必须全部 archive。"""
    bad = []
    for old_id, (dir_frag, _) in REASSIGNMENTS.items():
        dirs = _find_task_dirs(dir_frag)
        for d in dirs:
            task = _load_json(d / "task.json")
            if task.get("meta", {}).get("phase") != "archive":
                bad.append((old_id, str(d), task.get("meta", {}).get("phase")))
    return {"all_archived": not bad, "violations": bad}


def check_deferred() -> dict:
    """待办组（doctor 报但不在 REASSIGNMENTS）必须含活跃任务。"""
    dups = _doctor_duplicates()
    reassigned_ids = set(REASSIGNMENTS.keys())
    deferred = [g for g in dups if g["task_id"] not in reassigned_ids]
    no_active = []
    for g in deferred:
        has_active = any(
            _load_json(ROOT / p).get("meta", {}).get("active")
            for p in g["paths"]
        )
        if not has_active:
            no_active.append(g["task_id"])
    return {
        "deferred_count": len(deferred),
        "all_have_active": not no_active,
        "violations": no_active,
    }


def _rewrite_task_json(path: Path, old_id: str, new_id: str, new_record: str) -> None:
    task = _load_json(path)
    task["id"] = new_id
    task["meta"]["record"] = new_record
    with open(path, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=1)


def _reference_belongs_to_reassigned(referrer_slug: str | None, old_id: str) -> bool:
    """判定对旧 ID 的引用是否指向重分配方（上下文感知）。

    仅对 CONTEXTUAL_GROUPS（CDM/报表树 与 RPC 树 纠缠组）生效：
    - 引用者 slug 含 CDM 特征词 → 引用指向重分配方（CDM 链），须改新 ID。
    - 引用者 slug 含 RPC 特征词 → 引用指向保留方（RPC 链），保持旧 ID。
    非纠缠组：无保留方子任务、无 CDM/RPC 分叉，引用视为指向保留方，不改。
    """
    if old_id not in CONTEXTUAL_GROUPS:
        return False
    if not referrer_slug:
        return False
    if any(frag in referrer_slug for frag in RPC_FEATURES):
        return False
    return any(frag in referrer_slug for frag in CDM_FEATURES)


def _rewrite_references(old_id: str, new_id: str) -> int:
    """上下文感知替换 parent/children/dependencies 引用中的旧 ID。

    - 跳过 11 组含活跃任务的撞车（DEFERRED_IDS）：整组任务不改写。
    - 引用归属判定：CDM/报表链引用者 → 改向新 ID；RPC 链/非纠缠 → 保持。
    - 重分配方自身 task.json 的 parent 引用（若有）也按同样规则处理。
    """
    count = 0
    for path in TASKS_ROOT.glob("**/task.json"):
        task = _load_json(path)
        if task.get("id") in DEFERRED_IDS:
            continue
        referrer_slug = task.get("slug")
        belongs = _reference_belongs_to_reassigned(referrer_slug, old_id)

        changed = False
        if task.get("parent") == old_id and belongs:
            task["parent"] = new_id
            changed = True
        if belongs:
            old_children = task.get("children") or []
            task["children"] = [new_id if c == old_id else c for c in old_children]
            if task["children"] != old_children:
                changed = True
            old_deps = task.get("dependencies") or []
            task["dependencies"] = [new_id if d == old_id else d for d in old_deps]
            if task["dependencies"] != old_deps:
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(task, f, ensure_ascii=False, indent=1)
            count += 1
    return count


def _rename_task_dir(task_dir: Path, old_id: str, new_id: str) -> Path:
    """归档目录重命名：目录名含 `Txxxx-` 旧 ID 前缀时替换为新 ID 前缀。"""
    parent, name = task_dir.parent, task_dir.name
    if name.startswith(f"{old_id}-"):
        new_name = f"{new_id}-{name[len(old_id) + 1:]}"
        target = parent / new_name
        if not target.exists():
            task_dir.rename(target)
            return target
    return task_dir


def apply_plan(plan: list[dict]) -> dict:
    results = []
    for item in plan:
        task_dir = ROOT / item["task_dir"]
        task_path = task_dir / "task.json"
        old_id, new_id = item["old_id"], item["new_id"]
        old_record, new_record = item["old_record"], item["new_record"]

        _rewrite_task_json(task_path, old_id, new_id, new_record)
        refs_changed = _rewrite_references(old_id, new_id)
        renamed_dir = _rename_task_dir(task_dir, old_id, new_id)

        record_changes = []
        if old_record:
            old_r = RECORDS_ROOT / str(old_record)
            if old_r.is_dir():
                new_r = RECORDS_ROOT / str(new_record)
                old_r.rename(new_r)
                record_changes.append(f"{old_record} -> {new_record}")

        results.append({
            "old_id": old_id, "new_id": new_id,
            "task_dir": str(renamed_dir.relative_to(ROOT)),
            "record_changes": record_changes,
            "reference_files_changed": refs_changed,
        })
    return {"applied": len(results), "items": results}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="预览不改动")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--check-cover", action="store_true")
    ap.add_argument("--check-disposable", action="store_true")
    ap.add_argument("--check-deferred", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if args.check_cover:
        d = check_cover()
        print(json.dumps(d, ensure_ascii=False))
        return 0 if not d["uncovered"] else 1
    if args.check_disposable:
        d = check_disposable()
        print(json.dumps(d, ensure_ascii=False))
        return 0 if d["all_archived"] else 1
    if args.check_deferred:
        d = check_deferred()
        print(json.dumps(d, ensure_ascii=False))
        return 0 if d["all_have_active"] else 1

    plan = build_plan()
    if args.dry_run:
        out = {
            "mode": "dry-run",
            "reassignments": [
                {**item,
                 "dir_rename": str(ROOT / item["task_dir"]).rsplit("/", 1)[1].startswith(f"{item['old_id']}-")}
                for item in plan
            ],
        }
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0

    if args.apply:
        result = apply_plan(plan)
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    ap.error("请指定 --dry-run / --check-cover / --check-disposable / --check-deferred / --apply")
    return 2


if __name__ == "__main__":
    sys.exit(main())
