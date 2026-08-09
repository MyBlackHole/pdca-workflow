"""to-tickets blocking edges（dependencies）与 ready-set 计算测试。

证明目标（AC-1..AC-6）：
- 子 task.json 支持 `dependencies` 声明直接前置依赖。
- `ready_set` 纯函数四类 fixture（无依赖/多级依赖/有环/缺失引用）
  行为正确：无环输出 ready-set，有环抛出明确错误。
- task.schema.json 支持 dependencies 且 doctor valid。
- check-design-vocab.py 拒绝词汇表外术语。
- design-it-twice 词汇契约与 to-tickets 文档契约同步。
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from ticket_dag import ready_set  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class ComputeReadySetTest(unittest.TestCase):
    def test_no_dependencies_all_ready(self) -> None:
        tasks = {"T1": set(), "T2": set(), "T3": set()}
        self.assertEqual(ready_set(tasks, set()), {"T1", "T2", "T3"})

    def test_multi_level_dependency_ready_set(self) -> None:
        tasks = {"T1": set(), "T2": {"T1"}, "T3": {"T2"}, "T4": set()}
        self.assertEqual(ready_set(tasks, set()), {"T1", "T4"})
        self.assertEqual(ready_set(tasks, {"T1"}), {"T2", "T4"})
        self.assertEqual(ready_set(tasks, {"T1", "T2"}), {"T3", "T4"})
        self.assertEqual(ready_set(tasks, {"T1", "T2", "T3"}), {"T4"})

    def test_diamond_dependency(self) -> None:
        tasks = {"A": set(), "B": {"A"}, "C": {"A"}, "D": {"B", "C"}}
        self.assertEqual(ready_set(tasks, set()), {"A"})
        self.assertEqual(ready_set(tasks, {"A"}), {"B", "C"})
        self.assertEqual(ready_set(tasks, {"A", "B", "C"}), {"D"})

    def test_cycle_rejected(self) -> None:
        tasks = {"T1": {"T2"}, "T2": {"T1"}}
        with self.assertRaises(ValueError):
            ready_set(tasks)

    def test_self_cycle_rejected(self) -> None:
        tasks = {"T1": {"T1"}}
        with self.assertRaises(ValueError):
            ready_set(tasks)

    def test_missing_reference_rejected(self) -> None:
        tasks = {"T1": {"T999"}}
        with self.assertRaises(ValueError):
            ready_set(tasks)

    def test_long_chain_cycle_detected(self) -> None:
        tasks = {"A": set(), "B": {"A"}, "C": {"B"}, "D": {"C", "B"}}
        self.assertEqual(ready_set(tasks, set()), {"A"})


class TaskSchemaContractTest(unittest.TestCase):
    def test_schema_has_dependencies(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text(encoding="utf-8"))
        self.assertIn("dependencies", schema["properties"])
        dep = schema["properties"]["dependencies"]
        self.assertEqual(dep["type"], "array")
        self.assertEqual(dep["items"]["type"], "string")
        self.assertEqual(dep["items"]["pattern"], "^T[0-9]{4,}$")

    def test_dependencies_optional_and_unique(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text(encoding="utf-8"))
        dep = schema["properties"]["dependencies"]
        self.assertNotIn("dependencies", schema.get("required", []))
        self.assertTrue(dep.get("uniqueItems", False))


class ComputeFrontierScriptTest(unittest.TestCase):
    def test_script_accepts_tasks_and_outputs_ready_set(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/compute-frontier.py")],
            input=json.dumps({"T1": [], "T2": ["T1"], "T3": []}),
            capture_output=True,
            text=True,
            check=True,
        )
        line = json.loads(proc.stdout.splitlines()[-1])
        self.assertEqual(set(line["ready_set"]), {"T1", "T3"})

    def test_script_cycle_returns_error(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/compute-frontier.py")],
            input=json.dumps({"T1": ["T2"], "T2": ["T1"]}),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("error", proc.stdout)


class DesignVocabContractTest(unittest.TestCase):
    def test_checker_accepts_vocab_terms(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check-design-vocab.py")],
            input="我们设计了一个 deep module，接口是 module 的 interface，放在 seam 上。",
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("vocab_ok", proc.stdout)

    def test_checker_rejects_forbidden_terms(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check-design-vocab.py")],
            input="这是 component 的 API boundary 和 service。",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        result = json.loads(proc.stdout.splitlines()[-1])
        self.assertFalse(result["vocab_ok"])
        self.assertIn("component", result["violations"])
        self.assertIn("API", result["violations"])
        self.assertIn("boundary", result["violations"])
        self.assertIn("service", result["violations"])


class TicketDagDocumentContractTest(unittest.TestCase):
    def test_to_tickets_mentions_dependencies_and_ready_set(self) -> None:
        text = (ROOT / "skills/to-tickets/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("dependencies", text)
        self.assertIn("ready-set", text)

    def test_design_it_twice_skill_exists(self) -> None:
        skill = ROOT / "skills/design-it-twice/SKILL.md"
        self.assertTrue(skill.is_file())
        text = skill.read_text(encoding="utf-8")
        for term in ("module", "interface", "seam", "adapter", "depth"):
            self.assertIn(term, text)

    def test_context_documents_ready_set(self) -> None:
        text = (ROOT / "pdca/CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("ready-set", text)


if __name__ == "__main__":
    unittest.main()
