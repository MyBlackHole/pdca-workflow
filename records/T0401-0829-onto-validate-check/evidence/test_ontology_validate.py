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
    _write(tmp_path, "concept/foo.md", GOOD)
    r = _run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["ok"] is True


def test_type_mismatch_detected(tmp_path: Path) -> None:
    _write(tmp_path, "concept/bar.md", BAD_TYPE)
    r = _run(tmp_path)
    assert r.returncode == 1
    assert "TYPE_DIR_MISMATCH" in r.stdout


def test_dangling_detected(tmp_path: Path) -> None:
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
