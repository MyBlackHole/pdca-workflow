#!/usr/bin/env python3
# 本体投射[T2053]：ontology:concept/blocking-edges（依赖图与 ready-set）；本体是源、代码是投射。
"""to-tickets blocking edges 依赖图与 ready-set 计算。

提供可复用的纯函数：从 task.id -> {直接前置 task.id} 映射计算 ready-set
（所有直接前置已完成的任务集合），并做 DAG 无环/引用完整性校验。
供 compute-frontier.py 脚本与 tests/test_ticket_dag.py 共用。
"""

from __future__ import annotations

from typing import Iterator


def find_cycle(tasks: dict[str, set[str]]) -> list[str] | None:
    """三色标记法检测有向环，返回环路径（任取一个）；无环返回 None。

    tasks: {task_id: {直接前置 task_id}}。仅直接前置边；传递关系由
    ready_set 推导，不在此存储。
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {t: WHITE for t in tasks}
    stack: list[str] = []

    def dfs(node: str) -> list[str] | None:
        color[node] = GRAY
        stack.append(node)
        for nxt in tasks[node]:
            if color[nxt] == GRAY:
                cut = stack[stack.index(nxt):]
                return cut + [nxt]
            if color[nxt] == WHITE:
                found = dfs(nxt)
                if found:
                    return found
        color[node] = BLACK
        stack.pop()
        return None

    for node in tasks:
        if color[node] == WHITE:
            found = dfs(node)
            if found:
                return found
    return None


def validate(tasks: dict[str, set[str]]) -> None:
    """校验引用完整性与无环，违规抛 ValueError。"""
    all_ids = set(tasks)
    for src, deps in tasks.items():
        unknown = deps - all_ids
        if unknown:
            raise ValueError(f"缺失依赖引用: {sorted(unknown)}")
        if src in deps:
            raise ValueError(f"自环依赖: {src}")
    cycle = find_cycle(tasks)
    if cycle:
        raise ValueError(f"依赖环: {' -> '.join(cycle)}")


def ready_set(
    tasks: dict[str, set[str]],
    completed: set[str] | None = None,
) -> set[str]:
    """计算 ready-set：未完成且所有直接前置已完成的任务集合。

    先校验 DAG 合法（无环、引用完整），再计算。completed 缺省为空集。
    """
    validate(tasks)
    completed = completed or set()
    return {
        t
        for t in tasks
        if t not in completed and not (tasks[t] - completed)
    }


def ready_set_batches(
    tasks: dict[str, set[str]],
    batch_size: int = 0,
) -> list[list[str]]:
    """按依赖分批输出 ready-set 批次：每批都是当前"全部可并行"任务。

    顺序执行时第 i 批完成后再进入第 i+1 批。batch_size<=0 时每批为完整
    ready-set（不拆批）；>0 时每批至多 batch_size 个。
    """
    validate(tasks)
    remaining = set(tasks)
    completed: set[str] = set()
    batches: list[list[str]] = []
    while remaining:
        current = sorted(
            t for t in remaining if not (tasks[t] - completed)
        )
        if not current:
            raise ValueError("依赖环或遗漏前置导致 ready-set 为空，任务图不完整")
        take = current[:batch_size] if batch_size > 0 else current
        batches.append(take)
        completed.update(take)
        remaining.difference_update(take)
    return batches


def iter_tasks(dag: dict[str, list[str]]) -> Iterator[tuple[str, set[str]]]:
    """把 {id: [前置 id 列表]} 归一化为 {id: set}。"""
    for tid, deps in dag.items():
        yield tid, set(deps)
