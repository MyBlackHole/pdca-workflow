#!/usr/bin/env python3
"""Uniform atomic task creation entrypoint.

All task creation flows (triage, to-tickets, promotion, Act follow-up) must
route through this module so that task IDs and record identities are allocated
inside one repository-level critical section.

Contract: `create` allocates the next task ID, checks slug uniqueness, assigns
the immutable `meta.record`, creates `records/<record>/`, and writes
task.json / clarifications.jsonl / prd.md with create-only semantics. Any
failure cleans up what it created and leaves prior artifacts untouched.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

import fcntl

from pdca_core import load_json, repo_root, schema_issues
from ontology_reason import controlled_node_types, load_ontology

TASK_ID_RE = re.compile(r"^T[0-9]{4,}$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
TRANSITIONS = {"created", "plan", "do", "check", "act", "archive"}

# 本体节点类型词表（与 scripts/ontology-validate.py:TYPE_VOCAB 对齐）。
# 任务创建时可用 --ontology-node-type 显式声明本任务主体产出的节点类型，
# 使「任务类型 ↔ 本体节点类型」成为结构化关系，供拆分/计划/检索引用。
ONTOLOGY_NODE_TYPES = {
    "domain", "entity", "concept", "process", "role",
    "pattern", "principle", "pitfall", "fact", "decision",
}

# pdca-task 元概念节点 id；任务创建时默认锚定到此节点（消费该元概念）。
PDCA_TASK_NODE = "ontology:concept/pdca-task"


class TaskIdentityError(Exception):
    """A stable rejection carrying a machine-readable code."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def payload(self) -> dict[str, str]:
        return {"status": "rejected", "error": self.code, "path": self.path, "message": self.message}


@contextmanager
def _identity_lock(root: Path) -> Any:
    """Serialize ID reservation and directory creation across CLI processes."""

    digest = hashlib.sha256(str(root.resolve()).encode("utf-8")).hexdigest()
    path = Path(tempfile.gettempdir()) / f"pdca-task-identity-{digest}.lock"
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _write_new_file(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _next_task_id(root: Path) -> str:
    highest = 0
    for task_path in (root / "pdca" / "tasks").glob("**/task.json"):
        try:
            task = load_json(task_path)
        except (OSError, json.JSONDecodeError):
            continue
        task_id = task.get("id")
        if isinstance(task_id, str) and TASK_ID_RE.fullmatch(task_id):
            highest = max(highest, int(task_id[1:]))
    return f"T{highest + 1:04d}"


def _validate(root: Path, value: dict[str, Any], schema: str, path: str) -> None:
    issues = schema_issues(root, value, schema)
    if issues:
        first = issues[0]
        raise TaskIdentityError(first.code, f"{path}{first.path}", first.message)


def _record_from_id_and_slug(task_id: str, slug: str) -> str:
    return f"{task_id}-{slug}"


def _find_task_by_id(root: Path, task_id: str) -> dict[str, Any] | None:
    for task_path in (root / "pdca" / "tasks").glob("**/task.json"):
        try:
            task = load_json(task_path)
        except (OSError, json.JSONDecodeError):
            continue
        if task.get("id") == task_id:
            return task
    return None


def _inherit_ontology_meta(root: Path, parent: str | None) -> tuple[str | None, str | None]:
    """子任务默认继承父任务的本体片段与节点类型，使拆分沿本体边界对齐。"""
    if not parent:
        return None, None
    parent_task = _find_task_by_id(root, parent)
    if not parent_task:
        return None, None
    parent_meta = parent_task.get("meta", {}) or {}
    fragment = parent_meta.get("ontology_fragment")
    node_type = parent_meta.get("ontology_node_type")
    return (fragment if isinstance(fragment, str) else None,
            node_type if isinstance(node_type, str) else None)


def _validate_ontology_fragment(root: Path, fragment: str) -> None:
    """轻量校验：fragment 须指向仓库内存在的本体目录（非空、含本体资产）。"""
    target = (root / fragment).resolve()
    if not target.exists():
        raise TaskIdentityError(
            "ONTOLOGY_FRAGMENT_MISSING",
            "--ontology-fragment",
            f"ontology fragment path does not exist: {fragment}",
        )
    if not target.is_dir():
        raise TaskIdentityError(
            "ONTOLOGY_FRAGMENT_NOT_DIR",
            "--ontology-fragment",
            f"ontology fragment must be a directory: {fragment}",
        )


def _inherit_ontology_anchor(root: Path, parent: str | None) -> str | None:
    """子任务默认继承父任务的本体锚点（与 fragment/node_type 继承一致）。"""
    if not parent:
        return None
    parent_task = _find_task_by_id(root, parent)
    if not parent_task:
        return None
    return (parent_task.get("meta") or {}).get("ontology_anchor")


def _ontology_anchor_node(root: Path, anchor: str):
    """返回锚定节点 frontmatter；本体目录缺失或节点不存在则返回 None。"""
    ont_dir = root / "ontology"
    if not ont_dir.is_dir():
        return None
    return load_ontology(ont_dir).get(anchor)


def _validate_ontology_anchor(root: Path, anchor: str) -> None:
    """校验锚定节点存在且为 concept 类型（用于显式/继承锚点）。"""
    node = _ontology_anchor_node(root, anchor)
    if node is None:
        raise TaskIdentityError(
            "ONTOLOGY_ANCHOR_MISSING",
            "--ontology-anchor",
            f"anchor node not found in ontology: {anchor}",
        )
    if node.get("type") != "concept":
        raise TaskIdentityError(
            "ONTOLOGY_ANCHOR_TYPE",
            "--ontology-anchor",
            f"anchor must be a concept node, got {node.get('type')!r}",
        )


def create_task(
    root: Path,
    *,
    slug: str,
    title: str,
    scenario_type: str,
    created_at: str,
    parent: str | None = None,
    dependencies: tuple[str, ...] = (),
    extra_meta: dict[str, Any] | None = None,
    forced_record: str | None = None,
    initial_clarification: dict[str, Any] | None = None,
    initial_prd: str | None = None,
    task_root: Path | None = None,
    convergence: tuple[str, ...] | None = None,
    ontology_fragment: str | None = None,
    ontology_node_type: str | None = None,
) -> dict[str, Any]:
    if not re.fullmatch(r"^[0-9]{4}-[a-z0-9][a-z0-9-]*$", slug):
        raise TaskIdentityError("TASK_SLUG_INVALID", "--slug", "must be a strict PDCA task slug (MMDD-name)")
    if not title.strip():
        raise TaskIdentityError("TASK_TITLE_MISSING", "--title", "must be nonempty")
    if parent is not None and not TASK_ID_RE.fullmatch(parent):
        raise TaskIdentityError("PARENT_ID_INVALID", "--parent", "must be a strict task ID")
    if forced_record is not None and not SAFE_NAME.fullmatch(forced_record):
        raise TaskIdentityError("RECORD_INVALID", "--record", "must be a safe direct child name")
    parsed_created = _parse_local_datetime(created_at)

    with _identity_lock(root):
        return _create_task_unlocked(
            root,
            slug=slug,
            title=title,
            scenario_type=scenario_type,
            created_at=parsed_created,
            parent=parent,
            dependencies=dependencies,
            extra_meta=extra_meta,
            forced_record=forced_record,
            initial_clarification=initial_clarification,
            initial_prd=initial_prd,
            task_root=task_root,
            convergence=convergence,
            ontology_fragment=ontology_fragment,
            ontology_node_type=ontology_node_type,
        )


def _create_task_unlocked(
    root: Path,
    *,
    slug: str,
    title: str,
    scenario_type: str,
    created_at: str,
    parent: str | None = None,
    dependencies: tuple[str, ...] = (),
    extra_meta: dict[str, Any] | None = None,
    forced_record: str | None = None,
    initial_clarification: dict[str, Any] | None = None,
    initial_prd: str | None = None,
    task_root: Path | None = None,
    convergence: tuple[str, ...] | None = None,
    ontology_fragment: str | None = None,
    ontology_node_type: str | None = None,
) -> dict[str, Any]:
    tasks_root = root / "pdca" / "tasks"
    tasks_root.mkdir(parents=True, exist_ok=True)
    destination = (task_root or tasks_root) / slug
    if destination.exists():
        raise TaskIdentityError(
            "TASK_PATH_CONFLICT",
            destination.relative_to(root).as_posix(),
            "slug already exists",
        )
    task_id = _next_task_id(root)
    record = forced_record or _record_from_id_and_slug(task_id, slug)
    if forced_record is not None and forced_record != _record_from_id_and_slug(task_id, slug):
        raise TaskIdentityError(
            "RECORD_MISMATCH",
            "--record",
            "record identity must be derived from task ID and slug",
        )
    if not TASK_ID_RE.match(task_id):
        raise TaskIdentityError("TASK_ID_INVALID", "--task-id", "reserved ID is invalid")

    manifest_dir = root / "records" / record
    if manifest_dir.resolve().parent != (root / "records").resolve():
        raise TaskIdentityError("RECORD_PATH_INVALID", "--record", "record must be a direct child of records/")
    record_self = manifest_dir / "task.json"
    if record_self.exists():
        raise TaskIdentityError("RECORD_OCCUPIED", "--record", "record directory already owns a task")

    extra = dict(extra_meta or {})

    # 本体感知：若调用方未显式给出 ontology_fragment / ontology_node_type / ontology_anchor，
    # 则继承父任务（若存在且有值）；并做轻量校验，不破坏既有默认行为。
    inherited_fragment, inherited_node_type = _inherit_ontology_meta(root, parent)
    effective_fragment = ontology_fragment if ontology_fragment is not None else inherited_fragment
    effective_node_type = ontology_node_type if ontology_node_type is not None else inherited_node_type
    # 消费 pdca-task 元概念：默认把任务锚定到 ontology:concept/pdca-task，
    # 除非显式豁免（meta.ontology_exempt=true）；子任务继承父锚定。
    explicit_anchor = extra.get("ontology_anchor")
    exempt = extra.get("ontology_exempt") is True
    if exempt:
        effective_anchor = None
        is_default_anchor = False
    elif explicit_anchor is not None:
        effective_anchor = str(explicit_anchor)
        is_default_anchor = False
    else:
        parent_anchor = _inherit_ontology_anchor(root, parent)
        if parent_anchor is not None:
            effective_anchor = parent_anchor
            is_default_anchor = False
        else:
            effective_anchor = PDCA_TASK_NODE
            is_default_anchor = True
    if effective_anchor is not None:
        node = _ontology_anchor_node(root, effective_anchor)
        if node is not None and node.get("type") == "concept":
            extra["ontology_anchor"] = effective_anchor
        elif is_default_anchor:
            # 默认锚点（pdca-task）在本体缺失时（如自举期）跳过，不阻断创建
            pass
        else:
            if node is None:
                raise TaskIdentityError(
                    "ONTOLOGY_ANCHOR_MISSING", "--ontology-anchor",
                    f"anchor node not found in ontology: {effective_anchor}",
                )
            raise TaskIdentityError(
                "ONTOLOGY_ANCHOR_TYPE", "--ontology-anchor",
                f"anchor must be a concept node, got {node.get('type')!r}",
            )
    # 双层闸：research父仅生research叶，development父仅生development叶，跨层需显式ontology批注（T0520）
    if parent:
        parent_task = _find_task_by_id(root, parent)
        if parent_task:
            p_scen = (parent_task.get("meta") or {}).get("scenario_type")
            if p_scen and p_scen != scenario_type:
                # 跨层需显式 ontology: 批注于 title/convergence，不以继承 fragment 充数（防 research→development 直跳缺 research 叶）
                has_onto = "ontology:" in title.lower() or (convergence and any("ontology" in c.lower() for c in convergence))
                if not has_onto:
                    raise TaskIdentityError(
                        "SCENARIO_MISMATCH",
                        "--scenario-type",
                        f"parent {parent} is {p_scen} but child is {scenario_type}, cross-layer requires explicit ontology: batch (e.g., add 'ontology:xxx' to title/convergence)",
                    )
    if effective_fragment is not None:
        _validate_ontology_fragment(root, effective_fragment)
        extra["ontology_fragment"] = effective_fragment
    if effective_node_type is not None:
        allowed = controlled_node_types(ont_dir=root / "ontology")
        if effective_node_type not in allowed:
            raise TaskIdentityError(
                "ONTOLOGY_NODE_TYPE_INVALID",
                "--ontology-node-type",
                f"must be one of {sorted(allowed)}",
            )
        extra["ontology_node_type"] = effective_node_type

    convergence_items = list(convergence) if convergence else ["task identity is unique and immutable"]
    meta: dict[str, Any] = {
        "phase": "plan",
        "active": True,
        "scenario_type": scenario_type,
        "created_at": created_at,
        "convergence": convergence_items,
        "record": record,
        **extra,
    }
    task = {
        "id": task_id,
        "slug": slug,
        "title": title.strip(),
        "parent": parent,
        "children": [],
        "dependencies": list(dependencies),
        "status": "Pending",
        "meta": meta,
        "states": {
            "created": created_at,
            "plan": created_at,
            "do": None,
            "check": None,
            "act": None,
            "archive": None,
        },
    }
    _validate(root, task, "task.schema.json", "task.json")

    created_manifest = False
    try:
        (destination.parent).mkdir(parents=True, exist_ok=True)
        destination.mkdir()
        try:
            _write_new_file(destination / "task.json", canonical_bytes(task))
        except FileExistsError as exc:
            raise TaskIdentityError(
                "TASK_PATH_CONFLICT",
                destination.relative_to(root).as_posix(),
                "task.json already exists",
            ) from exc
        clarification = initial_clarification or {
            "source": "task_identity",
            "summary": f"created with record identity {record}",
            "at": created_at,
        }
        _write_new_file(destination / "clarifications.jsonl", canonical_bytes(clarification))
        prd = initial_prd or (
            f"# {title.strip()}\n\n"
            "## 验收标准\n\n"
            "- [ ] AC-1 示例验收\n\n"
            "## 关联本体节点\n\n"
            "（可选）本任务直接消费/产出/对齐的本体节点 id，一行一个，例如：\n"
            "```\n"
            "ontology:concept/xxx\n"
            "ontology:entity/yyy\n"
            "```\n\n"
            "## 拆分映射\n\n"
            "（有 meta.ontology_fragment 时必填，驱动本体关系树 WBS）\n"
            "- 章节示例 -> ontology:concept/pdca-task\n"
        )
        _write_new_file(destination / "prd.md", prd.encode("utf-8"))
        manifest_dir.mkdir(parents=True, exist_ok=True)
        created_manifest = True
        _write_new_file(manifest_dir / "task.json", canonical_bytes(task))
        _fsync_directory(destination)
        _fsync_directory(manifest_dir)
        _fsync_directory(tasks_root)
    except Exception:
        if created_manifest:
            (manifest_dir / "task.json").unlink(missing_ok=True)
            try:
                manifest_dir.rmdir()
            except OSError:
                pass
        for child in destination.iterdir() if destination.exists() else []:
            child.unlink(missing_ok=True)
        destination.rmdir()
        raise

    return {
        "status": "created",
        "task_id": task_id,
        "record": record,
        "path": destination.relative_to(root).as_posix(),
    }


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _parse_local_datetime(value: str) -> str:
    """Validate an ISO-8601 date-time and keep a deterministic local form."""
    try:
        from datetime import datetime

        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise TaskIdentityError("INVALID_TIMESTAMP", "--created-at", "must be an ISO-8601 date-time") from exc
    if parsed.tzinfo is None:
        raise TaskIdentityError("INVALID_TIMESTAMP", "--created-at", "must include a UTC offset")
    return parsed.isoformat(timespec="seconds")


def _parse_dependencies(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    items = tuple(part.strip() for part in value.split(",") if part.strip())
    for item in items:
        if not TASK_ID_RE.fullmatch(item):
            raise TaskIdentityError("DEPENDENCY_INVALID", "--dependencies", "each dependency must be a strict task ID")
    return items


def _parse_extra_meta(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise TaskIdentityError("EXTRA_META_INVALID", "--extra-meta", "must be a JSON object") from exc
    if not isinstance(parsed, dict):
        raise TaskIdentityError("EXTRA_META_INVALID", "--extra-meta", "must be a JSON object")
    return parsed


def _parse_create_args() -> dict[str, str | None]:
    arguments = sys.argv[2:]
    options: dict[str, str | None] = {}
    index = 0
    while index < len(arguments):
        option = arguments[index]
        if option.startswith("--"):
            name = option[2:]
            if index + 1 < len(arguments) and not arguments[index + 1].startswith("--"):
                options[name] = arguments[index + 1]
                index += 2
            else:
                options[name] = None
                index += 1
        else:
            raise TaskIdentityError("ARG_INVALID", option, "unexpected positional argument")
    return options


def _build_create(parse: Callable[[], dict[str, str | None]]) -> dict[str, Any]:
    options = parse()
    root = options.pop("root", None)
    forced_record = options.pop("record", None)
    resolved = repo_root(Path(root) if root else None)
    required = {"slug", "title", "created-at", "scenario-type"}
    values = {name: options.get(name) for name in required}
    missing = [name for name in sorted(required) if not values[name]]
    if missing:
        raise TaskIdentityError("ARG_MISSING", "--" + missing[0], "missing required option")
    slug = values["slug"]
    title = values["title"]
    scenario_type = values["scenario-type"]
    created_at = values["created-at"]
    convergence = options.get("convergence")
    assert slug is not None and title is not None and scenario_type is not None and created_at is not None
    return create_task(
        resolved,
        slug=slug,
        title=title,
        scenario_type=scenario_type,
        created_at=created_at,
        parent=options.get("parent"),
        dependencies=_parse_dependencies(options.get("dependencies")),
        extra_meta=_parse_extra_meta(options.get("extra-meta")),
        forced_record=forced_record,
        convergence=tuple(item.strip() for item in convergence.split("|")) if convergence else None,
        ontology_fragment=options.get("ontology-fragment"),
        ontology_node_type=options.get("ontology-node-type"),
    )


def _prompt_for_create() -> Callable[[], dict[str, Any]]:
    def command() -> dict[str, Any]:
        return _build_create(_parse_create_args)

    return command


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: task_identity.py create --slug ... --title ... [options]", file=sys.stderr)
        return 2
    subcommand = sys.argv[1]
    if subcommand != "create":
        print(f"unknown subcommand: {subcommand}", file=sys.stderr)
        return 2
    try:
        payload = _prompt_for_create()()
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return 0
    except TaskIdentityError as exc:
        print(json.dumps(exc.payload(), ensure_ascii=False, sort_keys=True), file=sys.stderr)
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"INTERNAL_ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())