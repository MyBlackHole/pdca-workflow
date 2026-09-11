from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

from .errors import RuntimeContractError
from .io import (
    atomic_write_json,
    confined_path,
    digest_file,
    digest_value,
    load_json,
    relative_path,
    validate_schema,
)
from .task import ExecutableTask


RELATION_RULE_ID = "ontology:concept/ontology-rule-non-dangling"


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise RuntimeContractError("ONTOLOGY_ASSET_INVALID", str(path), "ontology asset requires YAML frontmatter")
    parts = text.split("---", 2)
    try:
        value = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise RuntimeContractError("ONTOLOGY_ASSET_INVALID", str(path), "invalid YAML frontmatter") from exc
    if not isinstance(value, dict) or not isinstance(value.get("id"), str):
        raise RuntimeContractError("ONTOLOGY_ASSET_INVALID", str(path), "ontology asset requires an id")
    return value


def _relation_vocabulary(
    nodes: list[dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    metadata = by_id.get(RELATION_RULE_ID)
    if metadata is None:
        raise RuntimeContractError(
            "ONTOLOGY_RELATION_RULE_MISSING",
            RELATION_RULE_ID,
            "the active ontology relation rule is required",
        )
    rule_spec = metadata.get("rule_spec")
    relation_keys = rule_spec.get("reference_relation_keys") if isinstance(rule_spec, dict) else None
    if (
        not isinstance(relation_keys, list)
        or not relation_keys
        or not all(isinstance(item, str) and item.strip() for item in relation_keys)
        or len(set(relation_keys)) != len(relation_keys)
    ):
        raise RuntimeContractError(
            "ONTOLOGY_RELATION_RULE_INVALID",
            f"{RELATION_RULE_ID}/rule_spec/reference_relation_keys",
            "the active ontology rule must define unique non-empty reference relation keys",
        )
    rule_node = next(node for node in nodes if node["id"] == RELATION_RULE_ID)
    return {
        "governed_by": RELATION_RULE_ID,
        "source_path": rule_node["path"],
        "source_digest": rule_node["source_digest"],
        "relation_keys": relation_keys,
    }


def _authority_graph(
    root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    ontology_root = (root / "ontology").resolve()
    if not ontology_root.is_dir():
        raise RuntimeContractError("ONTOLOGY_AUTHORITY_MISSING", "ontology/", "active ontology graph is required")
    nodes: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for path in sorted(ontology_root.rglob("*.md")):
        if path.name == "README.md":
            continue
        metadata = _frontmatter(path)
        if metadata.get("status") != "active":
            continue
        node_id = metadata["id"]
        if node_id in by_id:
            raise RuntimeContractError("ONTOLOGY_NODE_DUPLICATE", str(path), f"duplicate ontology id: {node_id}")
        node = {
            "id": node_id,
            "type": metadata.get("type"),
            "path": relative_path(root, path),
            "source_digest": digest_file(path),
        }
        nodes.append(node)
        by_id[node_id] = metadata

    relation_vocabulary = _relation_vocabulary(nodes, by_id)
    edges: list[dict[str, str]] = []
    for source, metadata in by_id.items():
        relations = metadata.get("relations") or {}
        if not isinstance(relations, dict):
            continue
        for relation in relation_vocabulary["relation_keys"]:
            targets = relations.get(relation) or []
            if not isinstance(targets, list):
                continue
            for target in targets:
                if target in by_id:
                    edges.append({"source": source, "relation": relation, "target": target})
    nodes.sort(key=lambda item: item["id"])
    edges.sort(key=lambda item: (item["source"], item["relation"], item["target"]))
    return nodes, edges, relation_vocabulary


def _selected_subgraph(
    task: ExecutableTask,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
    selected_ids: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    known = {node["id"] for node in nodes}
    selected = set(selected_ids or [task.ontology_anchor])
    selected.add(task.ontology_anchor)
    unknown = sorted(selected - known)
    if unknown:
        raise RuntimeContractError(
            "BOUNDED_SUBGRAPH_NODE_UNKNOWN", "/selected_ids", f"unknown selected ontology nodes: {unknown}"
        )
    bounded_nodes = [
        {**node, "selection": "task_anchor" if node["id"] == task.ontology_anchor else "explicit_task_authority"}
        for node in nodes
        if node["id"] in selected
    ]
    bounded_edges = [edge for edge in edges if edge["source"] in selected and edge["target"] in selected]
    return bounded_nodes, bounded_edges


def _validate_execution_dag(leaves: list[dict[str, Any]]) -> None:
    ids = {leaf["id"] for leaf in leaves}
    if len(ids) != len(leaves):
        raise RuntimeContractError("EXECUTION_DAG_INVALID", "/action_bindings", "leaf ids must be unique")
    indegree = {identifier: 0 for identifier in ids}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for leaf in leaves:
        for dependency in leaf["depends_on"]:
            if dependency not in ids:
                raise RuntimeContractError(
                    "EXECUTION_DAG_INVALID", leaf["id"], f"unknown dependency: {dependency}"
                )
            outgoing[dependency].append(leaf["id"])
            indegree[leaf["id"]] += 1
    queue = deque(sorted(identifier for identifier, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        identifier = queue.popleft()
        visited += 1
        for target in outgoing[identifier]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(leaves):
        raise RuntimeContractError("EXECUTION_DAG_CYCLE", "/action_bindings", "execution dependencies must be acyclic")


def build_projection_manifest(
    task: ExecutableTask,
    selected_ids: list[str],
    action_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes, edges, relation_vocabulary = _authority_graph(task.root)
    bounded_nodes, bounded_edges = _selected_subgraph(task, nodes, edges, selected_ids)
    bounded_ids = {node["id"] for node in bounded_nodes}
    steps = {step["name"]: step for step in task.steps}

    seen_actions: set[int] = set()
    leaves: list[dict[str, Any]] = []
    for index, binding in enumerate(action_bindings):
        if not isinstance(binding, dict):
            raise RuntimeContractError("ACTION_BINDING_INVALID", f"/action_bindings/{index}", "binding must be an object")
        action_index = binding.get("action_index")
        step_name = binding.get("step_name")
        ontology_id = binding.get("ontology_id")
        depends_on = binding.get("depends_on", [])
        if not isinstance(action_index, int) or not 1 <= action_index <= len(task.required_actions):
            raise RuntimeContractError("ACTION_BINDING_INVALID", f"/action_bindings/{index}/action_index", "invalid action index")
        if action_index in seen_actions:
            raise RuntimeContractError("ACTION_BINDING_DUPLICATE", f"/action_bindings/{index}", "action is bound more than once")
        if step_name not in steps:
            raise RuntimeContractError("ACTION_BINDING_INVALID", f"/action_bindings/{index}/step_name", "unknown task step")
        if ontology_id not in bounded_ids:
            raise RuntimeContractError("ACTION_BINDING_INVALID", f"/action_bindings/{index}/ontology_id", "ontology node is outside the bounded subgraph")
        if not isinstance(depends_on, list) or not all(isinstance(item, str) for item in depends_on):
            raise RuntimeContractError("ACTION_BINDING_INVALID", f"/action_bindings/{index}/depends_on", "dependencies must be leaf ids")
        seen_actions.add(action_index)
        step = steps[step_name]
        leaves.append(
            {
                "id": f"action-{action_index:03d}",
                "ontology_node": ontology_id,
                "required_action_index": action_index,
                "required_action": task.required_actions[action_index - 1],
                "task_step": step_name,
                "completion_criterion": step["completion_criterion"],
                "depends_on": list(depends_on),
            }
        )
    expected = set(range(1, len(task.required_actions) + 1))
    if seen_actions != expected:
        raise RuntimeContractError(
            "ACTION_BINDING_INCOMPLETE", "/action_bindings", "every required action must be bound exactly once"
        )
    _validate_execution_dag(leaves)

    manifest: dict[str, Any] = {
        "schema": "pdca.ontology-projection/v1",
        "task_id": task.task_id,
        "ontology_role": task.ontology_role,
        "ontology_anchor": task.ontology_anchor,
        "execution_contract_digest": task.execution_contract_digest,
        "layers": {
            "authoritative_ontology_graph": {
                "nodes": nodes,
                "edges": edges,
                "relation_vocabulary": relation_vocabulary,
            },
            "bounded_task_subgraph": {"nodes": bounded_nodes, "edges": bounded_edges},
            "execution_tree_or_dag": {"projection": "dag", "leaves": leaves},
        },
    }
    manifest["digest"] = digest_value(manifest)
    validate_schema(task.root, manifest, "ontology-projection-manifest.schema.json", "PROJECTION_SCHEMA_INVALID")
    return manifest


def write_projection_manifest(path: Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(path, manifest)


def verify_projection_manifest(
    task: ExecutableTask,
    manifest: dict[str, Any] | Path,
    *,
    verify_sources: bool = True,
) -> dict[str, Any]:
    value = load_json(manifest, "PROJECTION_INVALID") if isinstance(manifest, Path) else manifest
    validate_schema(task.root, value, "ontology-projection-manifest.schema.json", "PROJECTION_SCHEMA_INVALID")
    expected_digest = digest_value({key: item for key, item in value.items() if key != "digest"})
    if value["digest"] != expected_digest:
        raise RuntimeContractError("PROJECTION_DIGEST_MISMATCH", "/digest", "projection manifest was modified")
    if value["task_id"] != task.task_id or value["ontology_role"] != task.ontology_role:
        raise RuntimeContractError("PROJECTION_TASK_MISMATCH", "/task_id", "projection belongs to another task or role")
    if value["execution_contract_digest"] != task.execution_contract_digest:
        raise RuntimeContractError("PROJECTION_CONTRACT_DRIFT", "/execution_contract_digest", "execution contract changed after projection")

    authority = value["layers"]["authoritative_ontology_graph"]
    current_nodes, current_edges, current_relation_vocabulary = _authority_graph(task.root)
    recorded_by_path = {node["path"]: node for node in authority["nodes"]}
    current_by_path = {node["path"]: node for node in current_nodes}
    for path in sorted(set(recorded_by_path) & set(current_by_path)):
        if recorded_by_path[path]["source_digest"] != current_by_path[path]["source_digest"]:
            raise RuntimeContractError("ONTOLOGY_SOURCE_DRIFT", path, "authority asset changed after projection")
    if (
        authority["nodes"] != current_nodes
        or authority["edges"] != current_edges
        or authority["relation_vocabulary"] != current_relation_vocabulary
    ):
        raise RuntimeContractError(
            "ONTOLOGY_AUTHORITY_GRAPH_DRIFT",
            "/layers/authoritative_ontology_graph",
            "projection must contain the complete active ontology graph",
        )

    bounded_ids = {node["id"] for node in value["layers"]["bounded_task_subgraph"]["nodes"]}
    leaves = value["layers"]["execution_tree_or_dag"]["leaves"]
    if [leaf["required_action"] for leaf in sorted(leaves, key=lambda item: item["required_action_index"])] != list(task.required_actions):
        raise RuntimeContractError("PROJECTION_ACTION_DRIFT", "/layers/execution_tree_or_dag", "required actions do not match")
    if any(leaf["ontology_node"] not in bounded_ids or not leaf["completion_criterion"] for leaf in leaves):
        raise RuntimeContractError("PROJECTION_TRACEABILITY_INVALID", "/layers/execution_tree_or_dag", "each leaf needs ontology and exit-criterion traceability")
    _validate_execution_dag(leaves)

    if verify_sources:
        for node in authority["nodes"]:
            path = confined_path(task.root, node["path"])
            if digest_file(path) != node["source_digest"]:
                raise RuntimeContractError("ONTOLOGY_SOURCE_DRIFT", node["path"], "authority asset changed after projection")
    return {
        "status": "passed",
        "task_id": task.task_id,
        "projection_digest": value["digest"],
        "authority_nodes": len(value["layers"]["authoritative_ontology_graph"]["nodes"]),
        "governed_semantic_edges": len(value["layers"]["authoritative_ontology_graph"]["edges"]),
        "relation_rule": authority["relation_vocabulary"]["governed_by"],
        "bounded_nodes": len(bounded_ids),
        "execution_leaves": len(leaves),
    }
