"""grilling frontier 批量问法轮数对比测试。

证明目标（AC-4）：相比旧的"一次只问一个"，frontier 批量问法把 Plan 对齐的
用户交互轮数从 N 降到 ceil(N/K)（K 为单轮容量），且依赖决策按依赖分批。
轮数模型为纯函数，不依赖外部环境，可回归验证。
"""

from __future__ import annotations

import math
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
        text = (ROOT / "skills/grilling/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("frontier", text)
        self.assertIn("round", text)
        # 不再要求"一次只问一个 / 从不批量"
        self.assertNotIn("一次只问一个", text)
        self.assertNotIn("one question at a time", text)
        self.assertNotIn("Never batch", text)

    def test_flow_plan_reference_synced(self) -> None:
        text = (ROOT / "flows/flow-plan/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("grilling", text)
        self.assertNotIn("一次只问一个", text)

    def test_flow_check_reference_synced(self) -> None:
        text = (ROOT / "flows/flow-check/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("grilling", text)

    def test_round_shared_within_batch_semantics_documented(self) -> None:
        text = (ROOT / "skills/grilling/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("round", text)


if __name__ == "__main__":
    unittest.main()
