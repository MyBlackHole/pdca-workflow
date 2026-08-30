"""T0417：消费 pdca-task 元概念驱动任务表达。

Seam: tests/test_pdca_task_consumption.py -> scripts/task_identity.py
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import task_identity
from scripts import ontology_reason

CREATED_AT = "2026-08-30T00:00:00+08:00"


def _cleanup(slug: str, record: str | None) -> None:
    for base in ("pdca/tasks", "records"):
        p = ROOT / base / slug
        if p.exists():
            shutil.rmtree(p)
    if record:
        rp = ROOT / "records" / record
        if rp.exists():
            shutil.rmtree(rp)


def test_anchor_default_points_to_pdca_task():
    slug = "0830-anchor-default"
    res = task_identity.create_task(
        ROOT, slug=slug, title="t", scenario_type="development", created_at=CREATED_AT
    )
    try:
        tj = json.loads((ROOT / "pdca" / "tasks" / slug / "task.json").read_text(encoding="utf-8"))
        assert tj["meta"]["ontology_anchor"] == "ontology:concept/pdca-task"
    finally:
        _cleanup(slug, res.get("record"))


def test_anchor_exempt_skips():
    slug = "0830-anchor-exempt"
    res = task_identity.create_task(
        ROOT, slug=slug, title="t", scenario_type="development",
        created_at=CREATED_AT, extra_meta={"ontology_exempt": True},
    )
    try:
        tj = json.loads((ROOT / "pdca" / "tasks" / slug / "task.json").read_text(encoding="utf-8"))
        assert "ontology_anchor" not in tj["meta"]
    finally:
        _cleanup(slug, res.get("record"))


def test_validate_anchor_missing(monkeypatch):
    monkeypatch.setattr(task_identity, "load_ontology", lambda d: {})
    try:
        task_identity._validate_ontology_anchor(ROOT, "ontology:concept/pdca-task")
    except task_identity.TaskIdentityError as exc:
        assert exc.code == "ONTOLOGY_ANCHOR_MISSING"
    else:
        raise AssertionError("expected ONTOLOGY_ANCHOR_MISSING")


def test_validate_anchor_wrong_type(monkeypatch):
    monkeypatch.setattr(
        task_identity, "load_ontology",
        lambda d: {"ontology:concept/pdca-task": {"type": "entity"}},
    )
    try:
        task_identity._validate_ontology_anchor(ROOT, "ontology:concept/pdca-task")
    except task_identity.TaskIdentityError as exc:
        assert exc.code == "ONTOLOGY_ANCHOR_TYPE"
    else:
        raise AssertionError("expected ONTOLOGY_ANCHOR_TYPE")


def test_validate_anchor_ok(monkeypatch):
    monkeypatch.setattr(
        task_identity, "load_ontology",
        lambda d: {"ontology:concept/pdca-task": {"type": "concept"}},
    )
    task_identity._validate_ontology_anchor(ROOT, "ontology:concept/pdca-task")


def test_controlled_node_types_from_ontology(monkeypatch):
    nodes = {"ontology:concept/ontology-asset": {"node_types": ["domain", "entity", "custom"]}}
    assert ontology_reason.controlled_node_types(nodes) == {"domain", "entity", "custom"}


def test_controlled_node_types_fallback():
    assert ontology_reason.controlled_node_types({}) == set(ontology_reason.FALLBACK_NODE_TYPES)


def test_node_type_rejected_when_not_in_ontology_vocab(monkeypatch):
    nodes = {
        "ontology:concept/pdca-task": {"type": "concept"},
        "ontology:concept/ontology-asset": {"node_types": ["domain", "entity"]},
    }
    monkeypatch.setattr(ontology_reason, "load_ontology", lambda d: nodes)
    slug = "0830-node-type"
    try:
        task_identity.create_task(
            ROOT, slug=slug, title="t", scenario_type="development",
            created_at=CREATED_AT, ontology_node_type="ghost",
        )
        raise AssertionError("expected ONTOLOGY_NODE_TYPE_INVALID")
    except task_identity.TaskIdentityError as exc:
        assert exc.code == "ONTOLOGY_NODE_TYPE_INVALID"
    finally:
        _cleanup(slug, None)


def test_child_inherits_parent_anchor():
    parent_slug = "0830-parent-anchor"
    child_slug = "0830-child-anchor"
    parent = task_identity.create_task(
        ROOT, slug=parent_slug, title="p", scenario_type="development", created_at=CREATED_AT
    )
    child = None
    try:
        child = task_identity.create_task(
            ROOT, slug=child_slug, title="c", scenario_type="development",
            created_at=CREATED_AT, parent=parent["task_id"],
        )
        ctj = json.loads((ROOT / "pdca" / "tasks" / child_slug / "task.json").read_text(encoding="utf-8"))
        assert ctj["meta"]["ontology_anchor"] == "ontology:concept/pdca-task"
    finally:
        _cleanup(child_slug, child.get("record") if child else None)
        _cleanup(parent_slug, parent.get("record"))
