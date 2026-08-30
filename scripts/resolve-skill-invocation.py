#!/usr/bin/env python3
"""Resolve and validate skill entry aliases and typed invocation edges."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from pdca_core import repo_root, schema_issues


CONTRACT_PATH = Path("pdca/skill-invocation-contract.json")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SKILL_REFERENCE_RE = re.compile(r"\$PDCA_HOME/ontology/domain/skill-([a-z][a-z0-9-]*)/")
ENTRY_ALIAS_RE = re.compile(r"`/([a-z][a-z0-9-]*)`")


class InvocationError(Exception):
    """A stable skill-invocation-contract rejection."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def error_payload(error: InvocationError) -> dict[str, str]:
    return {
        "schema": "pdca.skill-invocation-result/v1",
        "status": "error",
        "code": error.code,
        "path": error.path,
        "message": error.message,
    }


def safe_relative_path(root: Path, value: str, field: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise InvocationError("INVOCATION_CONTRACT_INVALID", field, "must stay inside the PDCA root") from exc
    return candidate


def read_asset(root: Path, path: Path, layer: str) -> dict[str, str]:
    relative = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise InvocationError("INVOCATION_ASSET_INVALID", relative, "asset is missing YAML frontmatter")
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise InvocationError("INVOCATION_ASSET_INVALID", relative, "asset frontmatter is invalid YAML") from exc
    if not isinstance(data, dict):
        raise InvocationError("INVOCATION_ASSET_INVALID", relative, "asset frontmatter must be a mapping")
    name = data.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise InvocationError("INVOCATION_ASSET_INVALID", relative, "asset name must be a lowercase skill name")
    invocation = data.get("invocation", "automatic")
    if invocation not in {"automatic", "manual"}:
        raise InvocationError("INVOCATION_ASSET_INVALID", relative, "invocation must be automatic or manual")
    if layer == "flow" and invocation != "automatic":
        raise InvocationError("INVOCATION_ASSET_INVALID", relative, "flows must use automatic invocation")
    return {"name": name, "invocation": invocation, "layer": layer, "file": relative}


def asset_catalog(root: Path) -> dict[str, dict[str, str]]:
    paths = [
        *((path, "flow") for path in sorted((root / "flows").glob("flow-*/SKILL.md"))),
        *((path, "skill") for path in sorted((root / "ontology/domain").glob("skill-*.md"))),
    ]
    catalog: dict[str, dict[str, str]] = {}
    for path, layer in paths:
        asset = read_asset(root, path, layer)
        if asset["name"] in catalog:
            raise InvocationError("INVOCATION_ASSET_DUPLICATE", asset["name"], "asset names must be unique")
        catalog[asset["name"]] = asset
    return catalog


def load_contract(root: Path) -> dict[str, Any]:
    path = root / CONTRACT_PATH
    if not path.is_file():
        raise InvocationError("INVOCATION_CONTRACT_MISSING", CONTRACT_PATH.as_posix(), "invocation contract is required")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InvocationError("INVOCATION_CONTRACT_INVALID", CONTRACT_PATH.as_posix(), "invocation contract is not valid JSON") from exc
    if not isinstance(value, dict):
        raise InvocationError("INVOCATION_CONTRACT_INVALID", CONTRACT_PATH.as_posix(), "invocation contract must be an object")
    issues = schema_issues(root, value, "skill-invocation-contract.schema.json")
    if issues:
        issue = issues[0]
        raise InvocationError("INVOCATION_CONTRACT_INVALID", f"{CONTRACT_PATH}{issue.path}", issue.message)
    return value


def require_asset(catalog: dict[str, dict[str, str]], name: str, field: str) -> dict[str, str]:
    asset = catalog.get(name)
    if asset is None:
        raise InvocationError("INVOCATION_ASSET_MISSING", field, f"asset is missing: {name}")
    return asset


def validate_contract(root: Path, contract: dict[str, Any], catalog: dict[str, dict[str, str]]) -> None:
    entry_relative = str(contract["entry_document"])
    entry_path = safe_relative_path(root, entry_relative, "entry_document")
    if not entry_path.is_file():
        raise InvocationError("INVOCATION_REFERENCE_MISSING", entry_relative, "entry document is missing")
    entry_asset = next((asset for asset in catalog.values() if asset["file"] == entry_relative), None)
    if entry_asset is None or entry_asset["layer"] != "skill" or entry_asset["invocation"] != "manual":
        raise InvocationError(
            "INVOCATION_ENTRY_DOCUMENT_INVALID",
            "entry_document",
            "entry document must be a manual skill entry",
        )

    aliases = contract["aliases"]
    alias_names = [item["alias"] for item in aliases]
    if len(set(alias_names)) != len(alias_names):
        raise InvocationError("INVOCATION_CONTRACT_INVALID", f"{CONTRACT_PATH}/aliases", "aliases must be unique")
    for index, alias in enumerate(aliases):
        target = require_asset(catalog, alias["target"], f"{CONTRACT_PATH}/aliases/{index}/target")
        if target["layer"] != "skill" or target["invocation"] != "manual":
            raise InvocationError(
                "INVOCATION_ALIAS_TARGET_INVALID",
                f"{CONTRACT_PATH}/aliases/{index}/target",
                "an alias must target a manual skill entry",
            )

    edges = contract["edges"]
    edge_keys = [(edge["from"], edge["to"], edge["document"]) for edge in edges]
    if len(set(edge_keys)) != len(edge_keys):
        raise InvocationError("INVOCATION_CONTRACT_INVALID", f"{CONTRACT_PATH}/edges", "edges must be unique")
    for index, edge in enumerate(edges):
        source = require_asset(catalog, edge["from"], f"{CONTRACT_PATH}/edges/{index}/from")
        target = require_asset(catalog, edge["to"], f"{CONTRACT_PATH}/edges/{index}/to")
        document_relative = str(edge["document"])
        document_path = safe_relative_path(root, document_relative, f"{CONTRACT_PATH}/edges/{index}/document")
        if not document_path.is_file():
            raise InvocationError("INVOCATION_REFERENCE_MISSING", document_relative, "edge document is missing")
        if source["file"] != document_relative:
            raise InvocationError(
                "INVOCATION_DOCUMENT_MISMATCH",
                f"{CONTRACT_PATH}/edges/{index}/document",
                "edge document must be the source asset document",
            )
        if target["invocation"] != "automatic":
            raise InvocationError(
                "INVOCATION_EDGE_FORBIDDEN",
                f"{CONTRACT_PATH}/edges/{index}",
                "flows and skills may only target automatic workers",
            )
        if source["layer"] == "flow" and source["invocation"] != "automatic":
            raise InvocationError(
                "INVOCATION_EDGE_FORBIDDEN",
                f"{CONTRACT_PATH}/edges/{index}",
                "flows must be automatic orchestrators",
            )


def verify_documents(root: Path, contract: dict[str, Any], catalog: dict[str, dict[str, str]]) -> dict[str, Any]:
    validate_contract(root, contract, catalog)
    declared_by_document: dict[str, set[str]] = {}
    for edge in contract["edges"]:
        declared_by_document.setdefault(edge["document"], set()).add(edge["to"])
    documents = sorted(asset["file"] for asset in catalog.values())
    for document in documents:
        declared_targets = declared_by_document.get(document, set())
        path = root / document
        references = set(SKILL_REFERENCE_RE.findall(path.read_text(encoding="utf-8")))
        undeclared = sorted(references - declared_targets)
        if undeclared:
            raise InvocationError(
                "INVOCATION_DOCUMENT_EDGE_UNDECLARED",
                document,
                f"document references undeclared workers: {', '.join(undeclared)}",
            )
        missing = sorted(declared_targets - references)
        if missing:
            raise InvocationError(
                "INVOCATION_DOCUMENT_EDGE_MISSING",
                document,
                f"contract edges are absent from document: {', '.join(missing)}",
            )

    entry_relative = str(contract["entry_document"])
    entry_path = root / entry_relative
    documented_aliases = set(ENTRY_ALIAS_RE.findall(entry_path.read_text(encoding="utf-8")))
    declared_aliases = {item["alias"] for item in contract["aliases"]}
    undeclared_aliases = sorted(documented_aliases - declared_aliases)
    if undeclared_aliases:
        raise InvocationError(
            "INVOCATION_ALIAS_UNDECLARED",
            entry_relative,
            f"entry document exposes undeclared aliases: {', '.join(undeclared_aliases)}",
        )
    missing_aliases = sorted(declared_aliases - documented_aliases)
    if missing_aliases:
        raise InvocationError(
            "INVOCATION_ALIAS_MISSING",
            entry_relative,
            f"contract aliases are absent from entry document: {', '.join(missing_aliases)}",
        )
    return {
        "schema": "pdca.skill-invocation-document-check/v1",
        "status": "ok",
        "asset_count": len(catalog),
        "edge_count": len(contract["edges"]),
        "alias_count": len(contract["aliases"]),
    }


def resolve_alias(contract: dict[str, Any], alias_name: str) -> dict[str, Any]:
    alias = next((item for item in contract["aliases"] if item["alias"] == alias_name), None)
    if alias is None:
        raise InvocationError("INVOCATION_ALIAS_UNKNOWN", "--alias", "alias is not configured")
    return {
        "schema": "pdca.skill-invocation-result/v1",
        "status": "ok",
        "alias": alias_name,
        "target": alias["target"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--alias")
    selection.add_argument("--verify-documents", action="store_true")
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        root = repo_root(args.root)
        contract = load_contract(root)
        catalog = asset_catalog(root)
        validate_contract(root, contract, catalog)
        payload = verify_documents(root, contract, catalog) if args.verify_documents else resolve_alias(contract, args.alias)
    except InvocationError as exc:
        emit(error_payload(exc))
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        error = InvocationError("INVOCATION_INTERNAL_ERROR", "/", "unable to resolve the invocation contract")
        emit(error_payload(error))
        print(f"{error.code}: {exc}", file=sys.stderr)
        return 1
    emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
