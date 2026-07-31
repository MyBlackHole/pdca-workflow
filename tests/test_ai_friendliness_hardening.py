from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE_SCRIPT = ROOT / "scripts/resolve-ai-friendliness-route.py"
HARNESS_SCRIPT = ROOT / "scripts/run-ai-friendliness-fixtures.py"
CONTENT_AUDIT_SCRIPT = ROOT / "scripts/audit-skill-content.py"


ROUTES = [
    ("development", "A", "path-a", ["A1", "A2", "A3", "A4", "A5"]),
    ("bugfix", "B", "path-b", ["B1", "B2", "B3", "B4"]),
    ("research", "C", "path-c", ["C1", "C2"]),
    ("documentation", "D", "path-d", ["D1", "D2"]),
    ("design", "E", "path-e", ["E1", "E2", "E3", "E4"]),
    ("review", "F", "path-f", ["F1", "F2", "F3"]),
]


def route_contract(routes: list[tuple[str, str, str, list[str]]] = ROUTES) -> dict:
    return {
        "schema": "pdca.ai-route-contract/v1",
        "flow_document": "flows/flow-do/SKILL.md",
        "routes": [
            {
                "scenario": scenario,
                "route_id": route_id,
                "anchor": anchor,
                "steps": steps,
            }
            for scenario, route_id, anchor, steps in routes
        ],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_route_root(root: Path) -> None:
    (root / "flows/flow-plan").mkdir(parents=True)
    (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
    (root / "flows/flow-do").mkdir(parents=True)
    (root / "flows/flow-do/SKILL.md").write_text(
        "# do\n\n" + "\n\n".join(f"## {anchor}" for _, _, anchor, _ in ROUTES) + "\n",
        encoding="utf-8",
    )
    shutil.copytree(ROOT / "schemas", root / "schemas")
    write_json(root / "pdca/ai-friendliness-route-contract.json", route_contract())


def run_json(arguments: list[str], *, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *arguments, "--root", str(root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


class AiFriendlinessHardeningTest(unittest.TestCase):
    def test_route_resolver_returns_contract_route_and_rejects_invalid_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)

            resolved = run_json([str(ROUTE_SCRIPT), "--scenario", "development"], root=root)
            self.assertEqual(0, resolved.returncode, resolved.stderr)
            payload = json.loads(resolved.stdout)
            self.assertEqual("ok", payload["status"])
            self.assertEqual("development", payload["scenario"])
            self.assertEqual(
                {"id": "A", "anchor": "path-a", "steps": ["A1", "A2", "A3", "A4", "A5"]},
                payload["route"],
            )

            invalid = run_json([str(ROUTE_SCRIPT), "--scenario", "audit"], root=root)
            self.assertNotEqual(0, invalid.returncode)
            self.assertEqual("ROUTE_SCENARIO_INVALID", json.loads(invalid.stdout)["code"])

    def test_route_contract_and_document_fail_closed_for_duplicate_or_missing_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)
            contract = route_contract()
            contract["routes"][1]["scenario"] = "development"
            write_json(root / "pdca/ai-friendliness-route-contract.json", contract)

            duplicate = run_json([str(ROUTE_SCRIPT), "--scenario", "development"], root=root)
            self.assertNotEqual(0, duplicate.returncode)
            self.assertEqual("ROUTE_CONTRACT_INVALID", json.loads(duplicate.stdout)["code"])

            write_json(root / "pdca/ai-friendliness-route-contract.json", route_contract())
            (root / "flows/flow-do/SKILL.md").write_text("# do\n", encoding="utf-8")
            missing_anchor = run_json([str(ROUTE_SCRIPT), "--verify-document"], root=root)
            self.assertNotEqual(0, missing_anchor.returncode)
            self.assertEqual("ROUTE_ANCHOR_MISSING", json.loads(missing_anchor.stdout)["code"])

    def test_document_reference_failure_uses_actual_contract_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)
            (root / "flows/flow-do/SKILL.md").unlink()

            result = run_json([str(ROUTE_SCRIPT), "--verify-document"], root=root)
            self.assertNotEqual(0, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual("ROUTE_REFERENCE_MISSING", payload["code"])
            self.assertEqual("flows/flow-do/SKILL.md", payload["path"])

    def test_public_harness_detects_contract_mutation_with_all_document_anchors_intact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)
            (root / "tests/fixtures").mkdir(parents=True)
            shutil.copy2(
                ROOT / "tests/fixtures/ai-friendliness-scenarios.json",
                root / "tests/fixtures/ai-friendliness-scenarios.json",
            )
            contract = route_contract()
            contract["routes"][0]["route_id"] = "B"
            contract["routes"][0]["anchor"] = "path-b"
            contract["routes"][0]["steps"] = ["B1", "B2", "B3", "B4"]
            contract["routes"][1]["route_id"] = "A"
            contract["routes"][1]["anchor"] = "path-a"
            contract["routes"][1]["steps"] = ["A1", "A2", "A3", "A4", "A5"]
            write_json(root / "pdca/ai-friendliness-route-contract.json", contract)

            result = run_json([str(HARNESS_SCRIPT), "--all"], root=root)
            self.assertNotEqual(0, result.returncode)
            payload = json.loads(result.stdout)
            development = next(item for item in payload["results"] if item["id"] == "development-normal")
            self.assertFalse(development["pass"])
            self.assertEqual("B", development["observed"])

    def test_public_harness_runs_real_lifecycle_success_and_transition_failures(self) -> None:
        completed = subprocess.run(
            ["python3", str(HARNESS_SCRIPT), "--all"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        repeated = subprocess.run(
            ["python3", str(HARNESS_SCRIPT), "--all"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, repeated.returncode, repeated.stderr)
        self.assertEqual(completed.stdout, repeated.stdout)
        payload = json.loads(completed.stdout)
        observed = {item["id"]: item["observed"] for item in payload["results"]}
        self.assertEqual("A", observed["execution-development-normal"])
        self.assertEqual("B", observed["execution-bugfix-normal"])
        self.assertEqual("EXECUTION_MARKER_ORDER_DRIFT", observed["execution-marker-order"])
        self.assertEqual("grill", observed["invocation-grill-alias"])
        self.assertEqual("INVOCATION_EDGE_FORBIDDEN", observed["invocation-manual-edge"])
        self.assertEqual("INVOCATION_ALIAS_UNDECLARED", observed["invocation-stale-alias"])
        self.assertEqual("archived", observed["lifecycle-success"])
        self.assertEqual("FINAL_CONFIRMATION_MISSING", observed["lifecycle-plan-confirmation"])
        self.assertEqual("PRD_MISSING", observed["lifecycle-do-prd"])
        self.assertEqual("EVIDENCE_MANIFEST_MISSING", observed["lifecycle-do-evidence"])
        self.assertEqual("CONVERGENCE_MAP_MISSING", observed["lifecycle-do-convergence"])
        self.assertEqual("CONCLUSION_MISSING", observed["lifecycle-check-conclusion"])
        self.assertEqual("VERDICT_MISSING", observed["lifecycle-check-verdict"])
        self.assertEqual("CHECK_CONFIRMATION_MISSING", observed["lifecycle-check-confirmation"])
        self.assertEqual("DISPOSITION_MISSING", observed["lifecycle-act-disposition"])

    def test_content_budget_update_cannot_hide_a_route_behavior_regression(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)
            (root / "tests/fixtures").mkdir(parents=True)
            shutil.copy2(
                ROOT / "tests/fixtures/ai-friendliness-scenarios.json",
                root / "tests/fixtures/ai-friendliness-scenarios.json",
            )
            baseline = {
                "schema": "pdca.skill-content-baseline/v1",
                "metric": "utf8_bytes",
                "assets": [
                    {
                        "file": path,
                        "bytes": len((root / path).read_bytes()),
                        "reason": "initial baseline",
                    }
                    for path in ("flows/flow-plan/SKILL.md", "flows/flow-do/SKILL.md")
                ],
            }
            write_json(root / "pdca/skill-content-baseline.json", baseline)
            contract = route_contract()
            contract["routes"][0].update({"route_id": "B", "anchor": "path-b", "steps": ["B1", "B2", "B3", "B4"]})
            contract["routes"][1].update({"route_id": "A", "anchor": "path-a", "steps": ["A1", "A2", "A3", "A4", "A5"]})
            write_json(root / "pdca/ai-friendliness-route-contract.json", contract)

            result = run_json([str(CONTENT_AUDIT_SCRIPT), "--check-budget"], root=root)
            self.assertNotEqual(0, result.returncode)
            codes = {item["code"] for item in json.loads(result.stdout)["budget"]["issues"]}
            self.assertIn("CONTENT_FIXTURE_FAILED", codes)

    def test_content_budget_rejects_growth_and_allows_explicit_reasoned_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)
            flow_plan = root / "flows/flow-plan/SKILL.md"
            flow_do = root / "flows/flow-do/SKILL.md"
            baseline = {
                "schema": "pdca.skill-content-baseline/v1",
                "metric": "utf8_bytes",
                "assets": [
                    {
                        "file": "flows/flow-plan/SKILL.md",
                        "bytes": len(flow_plan.read_bytes()),
                        "reason": "initial baseline",
                    },
                    {
                        "file": "flows/flow-do/SKILL.md",
                        "bytes": len(flow_do.read_bytes()),
                        "reason": "initial baseline",
                    },
                ],
            }
            write_json(root / "pdca/skill-content-baseline.json", baseline)

            initial = run_json([str(CONTENT_AUDIT_SCRIPT), "--check-budget"], root=root)
            self.assertEqual(0, initial.returncode, initial.stderr)
            self.assertEqual("passed", json.loads(initial.stdout)["budget"]["status"])

            flow_do.write_text(flow_do.read_text(encoding="utf-8") + "extra required detail\n", encoding="utf-8")
            exceeded = run_json([str(CONTENT_AUDIT_SCRIPT), "--check-budget"], root=root)
            self.assertNotEqual(0, exceeded.returncode)
            codes = {item["code"] for item in json.loads(exceeded.stdout)["budget"]["issues"]}
            self.assertIn("CONTENT_BUDGET_EXCEEDED", codes)

            baseline["assets"][1]["bytes"] = len(flow_do.read_bytes())
            baseline["assets"][1]["reason"] = "Adds a required recovery instruction"
            write_json(root / "pdca/skill-content-baseline.json", baseline)
            approved = run_json([str(CONTENT_AUDIT_SCRIPT), "--check-budget"], root=root)
            self.assertEqual(0, approved.returncode, approved.stderr)
            self.assertEqual("passed", json.loads(approved.stdout)["budget"]["status"])

    def test_content_budget_fails_closed_for_missing_baseline_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_route_root(root)
            write_json(
                root / "pdca/skill-content-baseline.json",
                {
                    "schema": "pdca.skill-content-baseline/v1",
                    "metric": "utf8_bytes",
                    "assets": [
                        {
                            "file": "flows/flow-plan/SKILL.md",
                            "bytes": len((root / "flows/flow-plan/SKILL.md").read_bytes()),
                            "reason": "initial baseline",
                        }
                    ],
                },
            )

            result = run_json([str(CONTENT_AUDIT_SCRIPT), "--check-budget"], root=root)
            self.assertNotEqual(0, result.returncode)
            codes = {item["code"] for item in json.loads(result.stdout)["budget"]["issues"]}
            self.assertIn("CONTENT_BASELINE_ASSET_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
