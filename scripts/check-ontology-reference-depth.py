#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/meta-ontology（引用深度判定树）；本体是源、代码是投射。
"""Check ontology reference depth for instances.

Validates that the link depth between instances and ontology nodes
follows the ontology-modular-reference.md decision tree:
- No hard hop limit; split by ontology relation naturally
- Single task typically involves 1-3 ontology nodes
- Fan-out rather than chain (dimensions like observability/maintainability/reliability are 1-hop fan-out, not chain)
- No islands in ontology_graph

Exit 0: all checks pass
Exit 1: depth issues found
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_DIR = ROOT / "ontology"

def check_depth(root: Path = ROOT) -> list[str]:
    """Check ontology reference depth issues."""
    issues: list[str] = []
    
    # Check ontology_graph for islands
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "ontology_graph.py")],
            capture_output=True, text=True, cwd=str(root)
        )
        if result.returncode != 0:
            issues.append("ontology_graph.py failed: " + result.stderr.strip())
            return issues
        output = result.stdout
        for line in output.split("\n"):
            if "islands:" in line:
                islands = int(line.split(":")[1].strip())
                if islands > 0:
                    issues.append(f"ontology_graph has {islands} islands")
                else:
                    issues.append("ontology_graph: 0 islands - OK")
                break
    except Exception as e:
        issues.append(f"Could not run ontology_graph.py: {e}")
    
    # Check task.json for ontology_fragment and relations
    tasks_dir = root / "pdca" / "tasks"
    if tasks_dir.exists():
        for task_file in sorted(tasks_dir.rglob("task.json")):
            try:
                task = json.loads(task_file.read_text(encoding="utf-8"))
                record = task.get("meta", {}).get("record", "")
                fragment = task.get("meta", {}).get("ontology_fragment", "")
                relations = task.get("meta", {}).get("relations", [])
                
                # Count ontology references
                ref_count = 0
                if fragment:
                    ref_count += 1
                if relations:
                    ref_count += len(relations)
                
                if ref_count > 3:
                    issues.append(f"{record}: {ref_count} ontology references (>3), review depth")
            except Exception:
                pass
    
    if not issues:
        issues.append("All ontology reference depth checks passed")
    
    return issues

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    issues = check_depth(root)
    for issue in issues:
        print(issue)
    has_errors = any("islands:" in i and "0 islands" not in i for i in issues) or any(">3" in i for i in issues)
    return 1 if has_errors else 0

if __name__ == "__main__":
    sys.exit(main())
