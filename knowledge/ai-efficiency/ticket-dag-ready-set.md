---
schema: pdca.asset/v1
id: knowledge.ai-efficiency.ticket-dag-ready-set
summary: to-tickets 显式依赖边（dependencies）+ ready-set 可执行任务集计算 + design-it-twice 强制词汇契约——把"可并行性"与"接口设计术语一致性"做成可回归验证的硬指标
tags: [ai-efficiency, to-tickets, dag, ready-set, design, pdca, contract]
scenarios: [plan, check]
phases: [plan, check]
source_ids: [T0232-0809-ticket-dag-design-twice]
---

# Ticket DAG & Ready-set 与 Design-it-twice 词汇契约

## 核心做法

### 1. Blocking edges（显式依赖边）

子任务拆解时在 `task.json` 声明 `dependencies: ["Txxxx"]`，仅存**直接前置**
（标准 DAG 语义），传递闭包由校验器推导。三个要点：

1. **仅直接边**。不冗余存储传递依赖，DAG 单源事实由校验器维护。
2. **ready-set = 可执行任务集**。所有"未完成且所有直接前置已完成"的任务集合；
   顺序执行时按 batches 分批（每批是当前全部可并行任务）。
3. **拆解后立即校验**。DAG 非法（有环/自环/缺失引用）→ 拒绝拆解产出。

> **术语消歧**：ready-set（可并行任务集）≠ grilling 的 frontier（当前可答
> 问题集合）。两者语义不同，CONTEXT.md 已分别记录。

### 2. Design-it-twice 强制词汇契约

接口设计时并行产出 2 个以上根本不同候选方案，用强制词汇表对比：
**module / interface / seam / adapter / depth**（含 leverage / locality）。
产出文档经 `scripts/check-design-vocab.py` 校验**只允许词汇表术语**，
拒绝 component / service / API / boundary。

## 可证明方式（与 T0230/T0231 同构）

- **DAG 校验**：`ready_set` 纯函数四类 fixture（无依赖/多级/有环/缺失引用），
  有环抛 ValueError；`scripts/compute-frontier.py` 可独立验证。
  见 `tests/test_ticket_dag.py`。
- **词汇契约**：`check-design-vocab.py` 拒绝词汇表外术语，与 T0231 source
  术语契约测试同构——契约由脚本强制、可回归验证。
- **实测**：全量 118 passed + 13 subtests，doctor valid，validate-convergence
  valid。契约校验器审查中发现并修复 API 大写漏检（`\b` 匹配须先小写化 term）。

## 日志约定（与门禁兼容）

- schema 的 `dependencies` 字段为**可选**（非 required）、uniqueItems；
  旧任务缺失即无依赖，不破坏既有任务。
- 同名文件登记证据时用 `--file` 指定存储名（如 design-it-twice.SKILL.md）。

## 复用场景

- 未来引入子任务实际并行调度：ready-set batches 直接驱动。
- 任何接口设计任务（Report Center、RPC 协议扩展）：design-it-twice + 词汇契约。
- 依赖关系显式化的其他拆解场景。
