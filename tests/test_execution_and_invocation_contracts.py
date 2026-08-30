from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_SCRIPT = ROOT / "scripts/resolve-ai-execution-contract.py"
INVOCATION_SCRIPT = ROOT / "scripts/resolve-skill-invocation.py"
CONTENT_AUDIT_SCRIPT = ROOT / "scripts/audit-skill-content.py"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_asset(root: Path, relative: str, name: str, invocation: str, body: str) -> None:
    invocation_line = "" if invocation == "automatic" else f"invocation: {invocation}\n"
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {name} fixture asset\n"
        f"{invocation_line}"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )


def execution_contract() -> dict:
    return {
        "schema": "pdca.ai-execution-contract/v1",
        "flow_document": "ontology/process/flow-do.md",
        "routes": [
            {
                "scenario": "development",
                "route_id": "A",
                "route_anchor": "路径 A：development（软件功能开发）",
                "phases": [
                    {"id": "seam", "marker": "确认 Seam"},
                    {"id": "red", "marker": "先写失败测试"},
                    {"id": "minimal-change", "marker": "最小实现"},
                    {"id": "focused-verification", "marker": "定向验证"},
                    {"id": "full-verification", "marker": "全量验证"},
                    {"id": "code-review", "marker": "双轴审查"},
                ],
                "receipt_policy": {
                    "slice": ["focused-verification"],
                    "final": ["full-verification", "code-review"],
                },
            },
            {
                "scenario": "bugfix",
                "route_id": "B",
                "route_anchor": "路径 B：bugfix（Bug 修复）",
                "phases": [
                    {"id": "seam", "marker": "确认回归 Seam"},
                    {"id": "red", "marker": "先复现失败"},
                    {"id": "minimal-change", "marker": "最小修复"},
                    {"id": "focused-verification", "marker": "定向回归验证"},
                    {"id": "full-verification", "marker": "全量验证"},
                    {"id": "code-review", "marker": "双轴审查"},
                ],
                "receipt_policy": {
                    "slice": ["focused-verification"],
                    "final": ["full-verification", "code-review"],
                },
            },
        ],
    }


def execution_document() -> str:
    return """---
name: flow-do
description: execution fixture flow
---

## 路径 A：development（软件功能开发）

确认 Seam
先写失败测试
最小实现
定向验证
全量验证
双轴审查

## 路径 B：bugfix（Bug 修复）

确认回归 Seam
先复现失败
最小修复
定向回归验证
全量验证
双轴审查
"""


def make_execution_root(root: Path) -> None:
    (root / "ontology/process/flow-plan").mkdir(parents=True)
    (root / "ontology/process/flow-plan.md").write_text("# plan\n", encoding="utf-8")
    flow = root / "ontology/process/flow-do.md"
    flow.parent.mkdir(parents=True)
    flow.write_text(execution_document(), encoding="utf-8")
    shutil.copytree(ROOT / "schemas", root / "schemas", dirs_exist_ok=True)
    (root / "pdca").mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        ROOT / "pdca/ai-friendliness-route-contract.json",
        root / "pdca/ai-friendliness-route-contract.json",
    )
    write_json(root / "pdca/ai-execution-contract.json", execution_contract())


def invocation_contract() -> dict:
    return {
        "schema": "pdca.skill-invocation-contract/v1",
        "entry_document": "skills/ask-matt/SKILL.md",
        "aliases": [
            {"alias": "grill", "target": "grill"},
            {"alias": "triage", "target": "triage"},
        ],
        "edges": [
            {
                "from": "flow-plan",
                "to": "triage-work",
                "document": "ontology/process/flow-plan.md",
            },
            {
                "from": "grill",
                "to": "grilling",
                "document": "skills/grill/SKILL.md",
            },
            {
                "from": "triage",
                "to": "triage-work",
                "document": "skills/triage/SKILL.md",
            },
        ],
    }


def make_invocation_root(root: Path) -> None:
    write_asset(
        root,
        "ontology/process/flow-plan.md",
        "flow-plan",
        "automatic",
        "加载 `$PDCA_HOME/skills/triage-work/SKILL.md`。",
    )
    write_asset(
        root,
        "skills/ask-matt/SKILL.md",
        "ask-matt",
        "manual",
        "入口：`/triage`、`/grill`。",
    )
    write_asset(
        root,
        "skills/grill/SKILL.md",
        "grill",
        "manual",
        "加载 `$PDCA_HOME/skills/grilling/SKILL.md`。",
    )
    write_asset(root, "skills/grilling/SKILL.md", "grilling", "automatic", "执行逐轮 Grill。")
    write_asset(
        root,
        "skills/triage/SKILL.md",
        "triage",
        "manual",
        "加载 `$PDCA_HOME/skills/triage-work/SKILL.md`。",
    )
    write_asset(root, "skills/triage-work/SKILL.md", "triage-work", "automatic", "执行 triage。")
    shutil.copytree(ROOT / "schemas", root / "schemas", dirs_exist_ok=True)
    write_json(root / "pdca/skill-invocation-contract.json", invocation_contract())


def run_json(script: Path, arguments: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *arguments, "--root", str(root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def write_content_baseline(root: Path) -> None:
    paths = [
        *(root / "flows").glob("flow-*/SKILL.md"),
        *(root / "skills").glob("**/SKILL.md"),
    ]
    write_json(
        root / "pdca/skill-content-baseline.json",
        {
            "schema": "pdca.skill-content-baseline/v1",
            "metric": "utf8_bytes",
            "assets": [
                {
                    "file": path.relative_to(root).as_posix(),
                    "bytes": len(path.read_bytes()),
                    "reason": "fixture baseline",
                }
                for path in sorted(paths)
            ],
        },
    )


class ExecutionContractTest(unittest.TestCase):
    def test_resolves_test_first_contract_and_rejects_marker_order_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_execution_root(root)

            resolved = run_json(EXECUTION_SCRIPT, ["--scenario", "development"], root)
            self.assertEqual(0, resolved.returncode, resolved.stderr)
            payload = json.loads(resolved.stdout)
            self.assertEqual("ok", payload["status"])
            self.assertEqual(
                [
                    "seam",
                    "red",
                    "minimal-change",
                    "focused-verification",
                    "full-verification",
                    "code-review",
                ],
                [phase["id"] for phase in payload["route"]["phases"]],
            )

            flow = root / "ontology/process/flow-do.md"
            flow.write_text(execution_document().replace("确认 Seam\n先写失败测试", "先写失败测试\n确认 Seam"), encoding="utf-8")
            drift = run_json(EXECUTION_SCRIPT, ["--verify-document"], root)
            self.assertNotEqual(0, drift.returncode)
            self.assertEqual("EXECUTION_MARKER_ORDER_DRIFT", json.loads(drift.stdout)["code"])

    def test_rejects_unsupported_scenario_and_missing_actual_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_execution_root(root)

            invalid = run_json(EXECUTION_SCRIPT, ["--scenario", "research"], root)
            self.assertNotEqual(0, invalid.returncode)
            self.assertEqual("EXECUTION_SCENARIO_INVALID", json.loads(invalid.stdout)["code"])

            route_contract_path = root / "pdca/ai-friendliness-route-contract.json"
            route_contract = json.loads(route_contract_path.read_text(encoding="utf-8"))
            route_contract["routes"][0]["anchor"] = "路径 A：development（独立 contract 漂移）"
            write_json(route_contract_path, route_contract)
            misaligned = run_json(EXECUTION_SCRIPT, ["--scenario", "development"], root)
            self.assertNotEqual(0, misaligned.returncode)
            self.assertEqual("EXECUTION_ROUTE_ALIGNMENT_FAILED", json.loads(misaligned.stdout)["code"])

            shutil.copy2(ROOT / "pdca/ai-friendliness-route-contract.json", route_contract_path)
            (root / "ontology/process/flow-do.md").unlink()
            missing = run_json(EXECUTION_SCRIPT, ["--verify-document"], root)
            self.assertNotEqual(0, missing.returncode)
            self.assertEqual("EXECUTION_REFERENCE_MISSING", json.loads(missing.stdout)["code"])

    def test_rejects_noncanonical_schema_and_ambiguous_document_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_execution_root(root)

            duplicate_scenario = execution_contract()
            duplicate_scenario["routes"][1]["scenario"] = "development"
            write_json(root / "pdca/ai-execution-contract.json", duplicate_scenario)
            invalid_scenario = run_json(EXECUTION_SCRIPT, ["--scenario", "development"], root)
            self.assertNotEqual(0, invalid_scenario.returncode)
            self.assertEqual("EXECUTION_CONTRACT_INVALID", json.loads(invalid_scenario.stdout)["code"])

            noncanonical_phases = execution_contract()
            noncanonical_phases["routes"][0]["phases"][0], noncanonical_phases["routes"][0]["phases"][1] = (
                noncanonical_phases["routes"][0]["phases"][1],
                noncanonical_phases["routes"][0]["phases"][0],
            )
            write_json(root / "pdca/ai-execution-contract.json", noncanonical_phases)
            invalid_phases = run_json(EXECUTION_SCRIPT, ["--scenario", "development"], root)
            self.assertNotEqual(0, invalid_phases.returncode)
            self.assertEqual("EXECUTION_CONTRACT_INVALID", json.loads(invalid_phases.stdout)["code"])

            write_json(root / "pdca/ai-execution-contract.json", execution_contract())
            flow = root / "ontology/process/flow-do.md"
            flow.write_text(
                execution_document().replace("确认 Seam\n先写失败测试", "确认 Seam\n确认 Seam\n先写失败测试"),
                encoding="utf-8",
            )
            ambiguous = run_json(EXECUTION_SCRIPT, ["--verify-document"], root)
            self.assertNotEqual(0, ambiguous.returncode)
            self.assertEqual("EXECUTION_MARKER_AMBIGUOUS", json.loads(ambiguous.stdout)["code"])


class InvocationContractTest(unittest.TestCase):
    def test_resolves_alias_and_rejects_automatic_to_manual_edge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_invocation_root(root)

            alias = run_json(INVOCATION_SCRIPT, ["--alias", "grill"], root)
            self.assertEqual(0, alias.returncode, alias.stderr)
            self.assertEqual("grill", json.loads(alias.stdout)["target"])

            entry_contract = invocation_contract()
            entry_contract["entry_document"] = "skills/grilling/SKILL.md"
            write_json(root / "pdca/skill-invocation-contract.json", entry_contract)
            invalid_entry = run_json(INVOCATION_SCRIPT, ["--alias", "grill"], root)
            self.assertNotEqual(0, invalid_entry.returncode)
            self.assertEqual("INVOCATION_ENTRY_DOCUMENT_INVALID", json.loads(invalid_entry.stdout)["code"])

            contract = invocation_contract()
            contract["edges"][0]["to"] = "triage"
            write_json(root / "pdca/skill-invocation-contract.json", contract)
            rejected = run_json(INVOCATION_SCRIPT, ["--verify-documents"], root)
            self.assertNotEqual(0, rejected.returncode)
            self.assertEqual("INVOCATION_EDGE_FORBIDDEN", json.loads(rejected.stdout)["code"])

    def test_rejects_stale_alias_and_undeclared_document_edge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_invocation_root(root)

            ask_matt = root / "skills/ask-matt/SKILL.md"
            ask_matt.write_text(ask_matt.read_text(encoding="utf-8").replace("/grill", "/grill-me"), encoding="utf-8")
            stale_alias = run_json(INVOCATION_SCRIPT, ["--verify-documents"], root)
            self.assertNotEqual(0, stale_alias.returncode)
            self.assertEqual("INVOCATION_ALIAS_UNDECLARED", json.loads(stale_alias.stdout)["code"])

            make_invocation_root(root)
            flow = root / "ontology/process/flow-plan.md"
            flow.write_text(
                flow.read_text(encoding="utf-8") + "加载 `$PDCA_HOME/skills/grilling/SKILL.md`。\n",
                encoding="utf-8",
            )
            undeclared = run_json(INVOCATION_SCRIPT, ["--verify-documents"], root)
            self.assertNotEqual(0, undeclared.returncode)
            self.assertEqual("INVOCATION_DOCUMENT_EDGE_UNDECLARED", json.loads(undeclared.stdout)["code"])


class ContentAuditContractTest(unittest.TestCase):
    def test_budget_cannot_hide_execution_or_invocation_contract_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_execution_root(root)
            write_content_baseline(root)
            flow = root / "ontology/process/flow-do.md"
            flow.write_text(flow.read_text(encoding="utf-8").replace("确认 Seam", "丢失 Seam"), encoding="utf-8")

            execution = run_json(CONTENT_AUDIT_SCRIPT, ["--check-budget"], root)
            self.assertNotEqual(0, execution.returncode)
            execution_codes = {item["code"] for item in json.loads(execution.stdout)["budget"]["issues"]}
            self.assertIn("CONTENT_EXECUTION_CONTRACT_FAILED", execution_codes)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_invocation_root(root)
            write_content_baseline(root)
            contract = invocation_contract()
            contract["edges"][0]["to"] = "triage"
            write_json(root / "pdca/skill-invocation-contract.json", contract)

            invocation = run_json(CONTENT_AUDIT_SCRIPT, ["--check-budget"], root)
            self.assertNotEqual(0, invocation.returncode)
            invocation_codes = {item["code"] for item in json.loads(invocation.stdout)["budget"]["issues"]}
            self.assertIn("CONTENT_INVOCATION_CONTRACT_FAILED", invocation_codes)


if __name__ == "__main__":
    unittest.main()
