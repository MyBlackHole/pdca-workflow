from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_AUDIT = ROOT / "scripts/audit-skill-content.py"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_content_root(root: Path) -> Path:
    sentinel = root / "ontology/process/flow-plan.md"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("# plan\n", encoding="utf-8")
    skill = root / "skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: example\ndescription: fixture\n---\n# Example\n", encoding="utf-8")
    write_json(
        root / "pdca/skill-content-baseline.json",
        {
            "schema": "pdca.skill-content-baseline/v1",
            "metric": "utf8_bytes",
            "assets": [
                {
                    "file": "skills/example/SKILL.md",
                    "bytes": len(skill.read_bytes()),
                    "reason": "fixture baseline",
                }
            ],
        },
    )
    (root / "schemas").mkdir()
    (root / "schemas/skill-content-baseline.schema.json").write_bytes(
        (ROOT / "schemas/skill-content-baseline.schema.json").read_bytes()
    )
    return skill


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(CONTENT_AUDIT), "--check-budget", "--root", str(root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class AiFriendlinessHardeningTest(unittest.TestCase):
    def test_content_budget_rejects_growth_and_accepts_reasoned_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = make_content_root(root)
            self.assertEqual(0, run(root).returncode)
            skill.write_text(skill.read_text(encoding="utf-8") + "required detail\n", encoding="utf-8")
            rejected = run(root)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("CONTENT_BUDGET_EXCEEDED", {item["code"] for item in json.loads(rejected.stdout)["budget"]["issues"]})
            baseline_path = root / "pdca/skill-content-baseline.json"
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            baseline["assets"][0]["bytes"] = len(skill.read_bytes())
            baseline["assets"][0]["reason"] = "required recovery instruction"
            write_json(baseline_path, baseline)
            self.assertEqual(0, run(root).returncode)

    def test_content_budget_fails_closed_for_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_content_root(root)
            baseline_path = root / "pdca/skill-content-baseline.json"
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            baseline["assets"][0]["file"] = "skills/missing/SKILL.md"
            write_json(baseline_path, baseline)
            result = run(root)
            self.assertNotEqual(0, result.returncode)
            codes = {item["code"] for item in json.loads(result.stdout)["budget"]["issues"]}
            self.assertIn("CONTENT_BASELINE_ASSET_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
