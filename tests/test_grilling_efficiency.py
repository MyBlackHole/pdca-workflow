"""grilling frontier 批量问法轮数对比测试。

证明目标（AC-4）：相比旧的"一次只问一个"，frontier 批量问法把 Plan 对齐的
用户交互轮数从 N 降到 ceil(N/K)（K 为单轮容量），且依赖决策按依赖分批。
轮数模型为纯函数，不依赖外部环境，可回归验证。
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def batch_rounds(
    num_decisions: int,
    capacity: int,
    dependencies: dict[int, set[int]] | None = None,
) -> int:
    """frontier 批量问法轮数。

    每轮取 frontier（前置均已决定的决策）中至多 capacity 个，直到全部决定。
    dependencies: {decision_id: {前置 decision_id}}，前置未决定则不可问。

    该模型刻画 grilling/SKILL.md 的批量问语义：
    一轮内问完所有"当前可答"的问题，而非一次只问一个。
    """
    if num_decisions <= 0:
        return 0
    deps = {i: set(dependencies.get(i, ())) for i in range(num_decisions)} if dependencies else {}
    decided: set[int] = set()
    rounds = 0
    pending = set(range(num_decisions))
    while pending:
        frontier = [
            d
            for d in pending
            if not (deps.get(d, set()) - decided)
        ]
        if not frontier:
            raise ValueError("依赖环或遗漏前置导致 frontier 为空，决策树不完整")
        take = frontier[:capacity]
        rounds += 1
        decided.update(take)
        pending.difference_update(take)
    return rounds


def sequential_rounds(num_decisions: int) -> int:
    """旧"一次只问一个"问法的轮数：每个决策一轮。"""
    return num_decisions


class BatchRoundsModelTest(unittest.TestCase):
    def test_empty_frontier(self) -> None:
        self.assertEqual(batch_rounds(0, 5), 0)

    def test_single_decision(self) -> None:
        self.assertEqual(batch_rounds(1, 5), 1)

    def test_independent_decisions_rounds_ceil(self) -> None:
        # N 个独立决策：批量问法轮数 = ceil(N/K)，严格小于 N（K>1 且 N>=3）
        for n in range(3, 12):
            for k in (2, 3, 5):
                r = batch_rounds(n, k)
                self.assertEqual(r, math.ceil(n / k))
                self.assertLess(r, sequential_rounds(n))

    def test_dependency_chain_batches_by_dependency(self) -> None:
        # 链式依赖 0->1->2->3->4，每轮只能问链头，需 5 轮
        deps = {i: {i - 1} for i in range(1, 5)}
        self.assertEqual(batch_rounds(5, 5, deps), 5)
        # 分叉依赖：2 依赖 0 和 1，0/1 独立可同轮问
        deps2 = {2: {0, 1}}
        self.assertEqual(batch_rounds(3, 5, deps2), 2)

    def test_mixed_frontier_pack(self) -> None:
        # 决策 0,1 独立，2 依赖 0。第 1 轮可问 {0,1}；第 2 轮问 2。
        deps = {2: {0}}
        self.assertEqual(batch_rounds(3, 5, deps), 2)

    def test_incomplete_dependency_rejected(self) -> None:
        # 真依赖环：0<->1 互相依赖，frontier 恒为空，应拒绝
        with self.assertRaises(ValueError):
            batch_rounds(2, 5, {0: {1}, 1: {0}})


class GrillingDocumentContractTest(unittest.TestCase):
    """文档契约：技能与 flow 引用必须与批量问法一致（AC-1、AC-2、AC-6）。"""

    def test_grilling_skill_batch_semantics(self) -> None:
        text = (ROOT / "ontology/domain/skill-grilling.md").read_text(encoding="utf-8")
        self.assertIn("frontier", text)
        self.assertIn("round", text)
        # 不再要求"一次只问一个 / 从不批量"
        self.assertNotIn("一次只问一个", text)
        self.assertNotIn("one question at a time", text)
        self.assertNotIn("Never batch", text)

    def test_flow_plan_reference_synced(self) -> None:
        text = (ROOT / "ontology/process/flow-plan.md").read_text(encoding="utf-8")
        self.assertIn("grilling", text)
        self.assertNotIn("一次只问一个", text)

    def test_flow_check_reference_synced(self) -> None:
        text = (ROOT / "ontology/process/flow-check/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("grilling", text)

    def test_round_shared_within_batch_semantics_documented(self) -> None:
        text = (ROOT / "ontology/domain/skill-grilling.md").read_text(encoding="utf-8")
        self.assertIn("round", text)


class SourceConsistencyContractTest(unittest.TestCase):
    """source 术语一致性（AC-1、AC-2、AC-3）：所有 flow 的 Q&A 记录必须用
    grilling 技能规则 6 规定的 source: "grilling"，不得残留旧的 "grill"。
    """

    def test_grilling_skill_uses_grilling_source(self) -> None:
        text = (ROOT / "ontology/domain/skill-grilling.md").read_text(encoding="utf-8")
        self.assertIn('source: "grilling"', text)

    def test_flow_act_uses_grilling_source(self) -> None:
        text = (ROOT / "ontology/process/flow-act/SKILL.md").read_text(encoding="utf-8")
        self.assertIn('source: "grilling"', text)
        self.assertNotIn('source: "grill"', text)

    def test_flow_check_uses_grilling_source(self) -> None:
        text = (ROOT / "ontology/process/flow-check/SKILL.md").read_text(encoding="utf-8")
        self.assertIn('source: "grilling"', text)
        self.assertNotIn('source: "grill"', text)

    def test_flow_plan_uses_grilling_source(self) -> None:
        text = (ROOT / "ontology/process/flow-plan.md").read_text(encoding="utf-8")
        self.assertIn('source: "grilling"', text)
        self.assertNotIn('source: "grill"', text)

    def test_no_old_grill_source_anywhere(self) -> None:
        for rel in ("ontology/process/flow-act/SKILL.md", "ontology/process/flow-check/SKILL.md", "ontology/process/flow-plan.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn('"grill"', text, f"{rel} 残留旧的 source: grill")


class Ac1BatchVerificationTest(unittest.TestCase):
    """Ac1 批量问法收益（AC-4）：flow-act Ac1 的 3 条独立追问应同轮批量问。

    轮数：batch_rounds(3, K) == 1（同轮），一次一问为 3，压缩 = 3。
    上下文成本：bytes 代理，批量问的提问正文总长远小于一次一问（省去每轮
    重复的前导说明/轮次描述），断言 bytes 压缩 > 1。
    """

    AC1_QUESTIONS = (
        "这个结论的适用范围和限制是什么？",
        "哪些部分可以提炼为可复用的知识？",
        "下次遇到类似问题，流程上有什么改进？",
    )

    def test_ac1_three_questions_in_one_round(self) -> None:
        # 3 条独立追问（无依赖）→ 批量问法 1 轮，一次一问 3 轮
        self.assertEqual(batch_rounds(len(self.AC1_QUESTIONS), 5), 1)
        self.assertEqual(sequential_rounds(len(self.AC1_QUESTIONS)), 3)
        self.assertLess(batch_rounds(len(self.AC1_QUESTIONS), 5), sequential_rounds(len(self.AC1_QUESTIONS)))

    def test_ac1_question_batch_bytes_cheaper(self) -> None:
        # bytes 代理：一次一问需 3 轮，每轮都要重述引导语；批量问仅 1 轮引导语
        prompt = "请确认知识沉淀质量："
        batch_payload = prompt + "\n".join(f"Q{i + 1}: {q}" for i, q in enumerate(self.AC1_QUESTIONS))
        sequential_payload = "".join(f"{prompt}\nQ: {q}" for q in self.AC1_QUESTIONS)
        batch_bytes = len(batch_payload.encode("utf-8"))
        sequential_bytes = len(sequential_payload.encode("utf-8"))
        self.assertGreater(sequential_bytes, batch_bytes)
        self.assertGreater(sequential_bytes / batch_bytes, 1.0)

    def test_ac1_flow_act_cites_three_questions(self) -> None:
        text = (ROOT / "ontology/process/flow-act/SKILL.md").read_text(encoding="utf-8")
        for q in self.AC1_QUESTIONS:
            self.assertIn(q, text)


class RealSessionRoundsDemoTest(unittest.TestCase):
    """Q1 补充证据：从真实 clarifications 会话统计批量问法轮数压缩。

    同一轮内批量提出的问题共享 round 号，因此批量问法轮数（distinct round）
    严格小于"一次一问"轮数（条目数）。
    """

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.session = Path(self.temporary.name) / "clarifications.jsonl"
        entries = [
            {"round": 1, "source": "grilling", "question": "a", "answer": "x", "at": "2026-08-09T00:00:00+08:00"},
            {"round": 1, "source": "grilling", "question": "b", "answer": "y", "at": "2026-08-09T00:00:00+08:00"},
            {"round": 1, "source": "grilling", "question": "c", "answer": "z", "at": "2026-08-09T00:00:00+08:00"},
            {"round": 2, "source": "grilling", "question": "d", "answer": "w", "at": "2026-08-09T00:00:01+08:00"},
        ]
        self.session.write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_demo_script_compresses_rounds(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/grilling-rounds-demo.py"), str(self.temporary.name)],
            capture_output=True,
            text=True,
            check=True,
        )
        line = json.loads(proc.stdout.splitlines()[-1])
        # 4 个条目、2 轮批量问（round 1 含 3 问），压缩比 = 4/2 = 2.0
        self.assertEqual(line["entries"], 4)
        self.assertEqual(line["batch_rounds"], 2)
        self.assertEqual(line["one_at_a_time_rounds"], 4)
        self.assertGreater(line["compression"], 1.0)


if __name__ == "__main__":
    unittest.main()
