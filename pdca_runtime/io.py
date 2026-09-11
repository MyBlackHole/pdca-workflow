from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .errors import RuntimeContractError


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def load_json(path: Path, code: str = "JSON_INVALID") -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeContractError(code, str(path), "file is required and must be readable") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeContractError(code, str(path), f"invalid JSON: {exc.msg}") from exc


def validate_schema(root: Path, value: Any, schema_name: str, code: str) -> None:
    schema_path = root / "schemas" / schema_name
    schema = load_json(schema_path, "RUNTIME_SCHEMA_MISSING")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if not errors:
        return
    first = errors[0]
    pointer = "/" + "/".join(str(part) for part in first.absolute_path)
    raise RuntimeContractError(code, pointer, first.message)


def confined_path(root: Path, value: str, *, must_exist: bool = True) -> Path:
    if not value or Path(value).is_absolute():
        raise RuntimeContractError("PATH_OUTSIDE_ROOT", value, "path must be a non-empty repository-relative path")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeContractError("PATH_OUTSIDE_ROOT", value, "path must stay inside the repository") from exc
    if must_exist and not candidate.is_file():
        raise RuntimeContractError("ARTIFACT_MISSING", value, "referenced file does not exist")
    return candidate


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise RuntimeContractError("PATH_OUTSIDE_ROOT", str(path), "path must stay inside the repository") from exc


def current_task_path(task_dir: Path, path: Path, *, must_exist: bool = True) -> Path:
    """Resolve a runtime artifact path and confine it to the named task directory."""

    resolved_task = task_dir.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(resolved_task)
    except ValueError as exc:
        raise RuntimeContractError(
            "TASK_ARTIFACT_SCOPE_INVALID",
            str(path),
            "runtime artifact inputs and outputs must stay inside the current task directory",
        ) from exc
    if must_exist and not resolved.is_file():
        raise RuntimeContractError("ARTIFACT_MISSING", str(path), "referenced file does not exist")
    return resolved


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
