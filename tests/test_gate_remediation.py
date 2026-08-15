"""门禁合规修复测试（T0271，第七轮）。

覆盖：
- audit-gate-compliance.py 修正：check 阶段无 verdict 不误报、gate_exemption 豁免识别
- remediate-gate-compliance.py：dry-run 预览（不实际改动）、apply 补 verdict/豁免/清理
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT_AUDIT = ROOT / "scripts" / "audit-gate-compliance.py"
SCRIPT_REMEDIATE = ROOT / "scripts" / "remediate-gate-compliance.py"


def make_task(task_id: str, slug: str, phase: str,
              verdict: bool = False, exemption: bool = False) -> dict:
    meta = {
        "phase": phase,
        "active": True,
        "scenario_type": "development",
        "created_at": "2026-08-15T00:00:00+08:00",
        "convergence": ["fixture"],
        "record": f"R-{task_id}",
    }
    if verdict:
        meta["verdict"] = {"outcome": "confirmed", "reason": "fixture", "at": "2026-08-15T00:00:00+08:00"}
    if exemption:
        meta["gate_exemption"] = {"reason": "fixture exemption", "at": "2026-08-15T00:00:00+08:00"}
    return {
        "id": task_id,
        "slug": slug,
        "title": slug,
        "parent": None,
        "children": [],
        "status": "Completed",
        "meta": meta,
        "states": {
            "created": "2026-08-15T00:00:00+08:00",
            "plan": "2026-08-15T00:00:00+08:00",
            "do": "2026-08-15T00:00:00+08:00",
            "check": "2026-08-15T00:00:00+08:00",
            "act": "2026-08-15T00:00:00+08:00",
            "archive": "2026-08-15T00:00:00+08:00",
        },
    }


class RemediationFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "records").mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, rel: str, content: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def write_task(self, rel: str, task: dict) -> None:
        p = self.root / rel / "task.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

    def run_cli(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(script), "--root", str(self.root), *args],
            capture_output=True,
            text=True,
        )


class AuditCorrectionTest(RemediationFixture):
    """audit 脚本修正：check 阶段不误报 + 豁免识别。"""

    def build_tasks(self) -> None:
        # check 阶段无 verdict（进行中，不应判违规）
        self.write_task("pdca/tasks/active/0801-checking", make_task("T9301", "0801-checking", "check", verdict=False))
        # archive 无 verdict（真违规，有 receipts）
        self.write_task("pdca/tasks/archive/2026-08/0802-bad", make_task("T9302", "0802-bad", "archive", verdict=False))
        receipts_dir = self.root / "pdca/tasks/archive/2026-08/0802-bad/transition-receipts"
        receipts_dir.mkdir(parents=True, exist_ok=True)
        for name in ("plan-to-do", "do-to-check", "check-to-act", "act-to-archive"):
            (receipts_dir / f"{name}.json").write_text(
                json.dumps({"schema": "pdca.transition/v1", "task_id": "T9302"}), encoding="utf-8")
        # archive 无 verdict 但有豁免（不判违规）
        self.write_task("pdca/tasks/archive/2026-08/0803-exempt", make_task("T9303", "0803-exempt", "archive", verdict=False, exemption=True))

    def test_check_phase_not_flagged_and_exemption_recognized(self) -> None:
        self.build_tasks()
        result = subprocess.run(
            ["python3", str(SCRIPT_AUDIT), "--scan", str(self.root / "pdca/tasks"), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        by_id = {item["id"]: item for item in data["items"]}
        self.assertEqual(3, len(data["items"]))
        self.assertNotIn("gate_incomplete:no-verdict", by_id["T9301"]["issues"])
        self.assertIn("gate_incomplete:no-verdict", by_id["T9302"]["issues"])
        self.assertTrue(by_id["T9303"]["gate_exemption"])
        self.assertNotIn("gate_incomplete:no-verdict", by_id["T9303"]["issues"])


class RemediateDryRunTest(RemediationFixture):
    def build_fixture(self) -> None:
        # T0207 有 conclusion（可补 verdict）
        self.write_task("pdca/tasks/archive/2026-08/0803-fsck-scrub-rewrite-followup",
                        make_task("T0207", "0803-fsck-scrub-rewrite-followup", "archive", verdict=False))
        self.write("records/T0207-0803-fsck-scrub-rewrite-followup/conclusion.md",
                   "# T0207 结论\n\n## Verdict\n\n**complete**（V-T0207-001）——4 项 AC 收敛。\n\n## AC 收敛\n")
        # T0149 无 conclusion（豁免）
        self.write_task("pdca/tasks/archive/2026-07/T0149-0801-design-md-review",
                        make_task("T0149", "T0149-0801-design-md-review", "archive", verdict=False))
        # 嵌套副本
        self.write_task("pdca/tasks/archive/0801-btree-split-proptest",
                        make_task("T0174", "0801-btree-split-proptest", "archive", verdict=True))
        self.write_task("pdca/tasks/archive/0801-btree-split-proptest/0801-btree-split-proptest",
                        make_task("T0174", "0801-btree-split-proptest", "archive", verdict=True))
        # active 残留（archive + active）
        self.write_task("pdca/tasks/archive/2026-08/0804-cdm-report-center-analyse",
                        make_task("T0214", "0804-cdm-report-center-analyse", "archive", verdict=True))
        self.write_task("pdca/tasks/active/0804-cdm-report-center-analyse",
                        make_task("T0214", "0804-cdm-report-center-analyse", "archive", verdict=True))

    def test_dry_run_previews_without_changes(self) -> None:
        self.build_fixture()
        result = self.run_cli(SCRIPT_REMEDIATE, "--dry-run")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("[补 verdict] T0207", result.stdout)
        self.assertIn("V-T0207-001", result.stdout)
        self.assertIn("[豁免] T0149", result.stdout)
        self.assertIn("[删嵌套副本]", result.stdout)
        self.assertIn("[移 active 残留]", result.stdout)
        # dry-run 不改动：T0207 无 verdict、嵌套副本仍存在、active 残留仍存在
        task_path = self.root / "pdca/tasks/archive/2026-08/0803-fsck-scrub-rewrite-followup/task.json"
        self.assertNotIn("verdict", json.loads(task_path.read_text())["meta"])
        self.assertTrue((self.root / "pdca/tasks/archive/0801-btree-split-proptest/0801-btree-split-proptest/task.json").is_file())
        self.assertTrue((self.root / "pdca/tasks/active/0804-cdm-report-center-analyse/task.json").is_file())

    def test_apply_backfills_verdict_exemption_and_cleanup(self) -> None:
        self.build_fixture()
        result = self.run_cli(SCRIPT_REMEDIATE, "--apply")
        self.assertEqual(0, result.returncode, result.stderr)
        # T0207 verdict 补齐
        task_path = self.root / "pdca/tasks/archive/2026-08/0803-fsck-scrub-rewrite-followup/task.json"
        task = json.loads(task_path.read_text())
        self.assertEqual("V-T0207-001", task["meta"]["verdict"]["verdict_id"])
        # T0149 豁免标记
        ex_path = self.root / "pdca/tasks/archive/2026-07/T0149-0801-design-md-review/task.json"
        self.assertIn("gate_exemption", json.loads(ex_path.read_text())["meta"])
        # 嵌套副本删除、active 残留移除
        self.assertFalse((self.root / "pdca/tasks/archive/0801-btree-split-proptest/0801-btree-split-proptest").exists())
        self.assertFalse((self.root / "pdca/tasks/active/0804-cdm-report-center-analyse").exists())
        # 主目录保留
        self.assertTrue((self.root / "pdca/tasks/archive/0801-btree-split-proptest/task.json").is_file())
        self.assertTrue((self.root / "pdca/tasks/archive/2026-08/0804-cdm-report-center-analyse/task.json").is_file())

    def test_requires_exactly_one_mode(self) -> None:
        result = self.run_cli(SCRIPT_REMEDIATE)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must specify exactly one of --dry-run or --apply", result.stderr)


if __name__ == "__main__":
    unittest.main()
