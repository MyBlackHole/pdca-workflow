#!/usr/bin/env python3
"""Seam: tests/test_ontology_validate.py -> scripts/ontology-validate.py

Validates that ontology-validate.py detects contract violations and passes clean assets.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "ontology-validate.py"

GOOD = """---
schema: pdca.asset/v1
id: ontology:concept/foo
type: concept
layer: Knowledge
summary: foo
status: active
attributes:
  - name: x
    desc: d
    constraint: c
    testable_signal: ts
relations:
  specializes: []
---
body
"""

BAD_TYPE = """---
schema: pdca.asset/v1
id: ontology:concept/bar
type: pattern
layer: Knowledge
summary: bar
status: active
attributes: []
---
body
"""

DANGLING = """---
schema: pdca.asset/v1
id: ontology:concept/baz
type: concept
layer: Knowledge
summary: baz
status: active
attributes:
  - name: x
    desc: d
    constraint: c
    testable_signal: ts
relations:
  specializes: ["ontology:concept/missing"]
---
body
"""


RULE_IDS = [
    "ontology:concept/ontology-rule-type-controlled",
    "ontology:concept/ontology-rule-non-dangling",
    "ontology:concept/ontology-rule-acyclic",
    "ontology:concept/ontology-rule-attr-testable",
    "ontology:concept/ontology-rule-richness",
    "ontology:concept/ontology-rule-guides-range",
]

def _ensure_rules(tmp: Path) -> None:
    for rid in RULE_IDS:
        typ, slug = rid.split(":")[1].split("/", 1)
        p = tmp / typ / f"{slug}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        # 用无依赖 stub 覆盖，避免真实文件的 specializes 链缺失；键名须与真实 rule_spec 一致
        stub = f"---\nschema: pdca.asset/v1\nid: {rid}\ntype: concept\nlayer: Knowledge\nstatus: active\nsummary: stub\nrule_spec:\n  allowed_types: [domain, entity, concept, process, role, pattern, principle, pitfall, fact, decision]\n  reference_relation_keys: [specializes, composed_of, configured_by, guides, relates_to]\n  graph_relation_keys: [specializes, composed_of]\n  extra_reference_fields: [domain]\n  attribute_test_field: testable_signal\n  knowledge_types: [pattern, principle, pitfall, fact, decision]\n  required_relations: [guides, relates_to]\n  target_types: [domain, entity]\n  composed_of_range: [entity, concept]\n  configured_by_target: ontology:entity/tls-configuration\n---\nstub\n"
        p.write_text(stub, encoding="utf-8")


def _write(tmp: Path, rel: str, text: str) -> None:
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _run(tmp: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--ontology-dir", str(tmp), "--format", "json"],
        capture_output=True, text=True,
    )


def test_clean_passes(tmp_path: Path) -> None:
    _ensure_rules(tmp_path)
    _write(tmp_path, "concept/foo.md", GOOD)
    r = _run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["ok"] is True


def test_type_mismatch_detected(tmp_path: Path) -> None:
    _ensure_rules(tmp_path)
    _write(tmp_path, "concept/bar.md", BAD_TYPE)
    r = _run(tmp_path)
    assert r.returncode == 1
    assert "TYPE_DIR_MISMATCH" in r.stdout


def test_dangling_detected(tmp_path: Path) -> None:
    _ensure_rules(tmp_path)
    _write(tmp_path, "concept/baz.md", DANGLING)
    r = _run(tmp_path)
    assert r.returncode == 1
    assert "DANGLING_REF" in r.stdout


if __name__ == "__main__":
    fails = 0
    for name in ("test_clean_passes", "test_type_mismatch_detected", "test_dangling_detected"):
        with tempfile.TemporaryDirectory() as d:
            try:
                globals()[name](Path(d))
                print(f"PASS {name}")
            except AssertionError as exc:
                fails += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if fails else 0)
