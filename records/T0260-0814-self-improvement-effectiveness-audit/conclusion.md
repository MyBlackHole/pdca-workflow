---
schema: pdca.asset/v1
id: T0260-0814-self-improvement-effectiveness-audit
phase: check
source_ids: [audit-metrics, independent-reference-set, deterministic-verification, research-report, convergence-map]
---

## 上下文

T0260 的顶层目标是提升本项目使用 AI 的效率，并要求所有优化判断由真实、非 fixture 的使用记录支持。同时审核 T0159 建立的 Flow Issue 记录方式是否能发现、定位和推动真实问题，而不是只积累记录。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 真实任务产物足以识别一批非猜测的 AI 效率问题 | **成立但有边界**：建立 5 项目的性独立参照集，识别 4 个候选方向；真实 token、耗时、工具调用因无结构化遥测而保持 unknown。 |
| occurrence 能持续发现这些真实效率问题 | **部分成立**：T0164→T0166 是真实正例；参照集其余 4 项未被直接捕获。 |
| backlog 能消费 cutover 后的真实 occurrence | **不成立**：正式 backlog 仅覆盖 34/199 事件；隔离全量重建因 EVENT_PATH_MISMATCH 被拒绝。 |
| Flow Issue 能进入真实治理与跨周期效果验证 | **不成立**：decision、candidate、improvement_source task 和 effectiveness verdict 均为 0。 |
| 当前实现仍能通过确定性合约 | **成立**：12/12 单测、8/8 fixture 通过，但不外推真实运行有效性。 |

## 分析

### PRD 验收

AC-1 至 AC-12 均由已登记的非 convergence-map 证据覆盖；`validate-convergence.py` 返回 `valid: true`。审计任务本身完整完成，`partial` 是对被审计机制的结果判定。

### 记录发现能力：partial

机制不是完全“白记录”。T0164 的 `PLAN_TO_DO_BEFORE_FINAL_CONFIRMATION` 与 `CONVERGENCE_PLACEHOLDER` occurrence 被 T0166 直接引用并促成真实门禁、doctor 修复，满足“至少发现一个经独立证实且可行动的问题”的最低价值门槛。

但它不能判为 effective：197/199 事件来自 transition audit，198/199 是 conformance deviation；T0230/T0231 的真实交互轮次改进等问题没有被捕获。正式 backlog 覆盖率只有 17.09%，且当前无法从全部事实重建。

### 完整自我提升闭环：partial

真实 occurrence 在持续产生，也发生过人工消费后的改进；但正式 `decision → candidate → Improvement Task → post-change observation → effectiveness verdict` 没有一次真实运行。T0166 是人工路径，不带 `improvement_source`，也没有 effectiveness verdict，不能冒充 T0159 的完整闭环。

### 首个阻断点

当前最先阻断闭环的是 task/record identity 完整性：23 个 task ID 被多个不同 slug 使用，5 个事件目录与 payload record_id 不一致，全量聚合 fail-closed。二者相关但尚未证明唯一因果，根因需在后续候选中用原子分配与并发测试验证。

### 候选顺序

1. P0：唯一且并发安全的 task/record identity 合约。
2. P1：backlog 新鲜度、可重建性和治理消费者门禁。
3. P2：绑定真实 task outcome 的交互、返工、恢复与可用 runner 遥测。
4. P3：不可变事件保留，派生层按 attempt 归并并绑定 resolution。

## 失败原因（仅 rejected/partial）

- 独立参照集有明确漏报，记录范围不足以覆盖 AI 使用效率。
- 正式 backlog 陈旧，且全量事实包含路径/record_id 不一致，无法重建。
- 153/199 事件位于同 record、同秒 burst，缺少 attempt/resolution 关系，系统性问题与已现场修复的瞬态失败难以区分。
- 仓库没有绑定 task identity 的 token、elapsed time 或 tool-call telemetry。
- 治理与效果验证产物为零，完整闭环仅在 fixture 中成立。

## 适用边界

- 5 项参照集是目的性真实案例，不是统计抽样；`1/5` 不外推为全仓库召回率。
- 任务 ID 冲突可能包含旧迁移或复制产物，本结论只断言冲突与聚合失败事实，不把分配器作为已证实唯一根因。
- 最终 confirmed 的任务中出现的门禁事件不自动等于 false positive；它们可能帮助现场恢复，但现有记录无法证明其后续解决关系。
- 没有仓库内 receipt 的外部消费者或遥测不作为存在证据。

## 下一轮建议

- 先将 P0 形成独立 Improvement Candidate，冻结冲突/mismatch/聚合状态 baseline，并验证新任务原子 ID 分配及 event path 不变量。
- P0 恢复投影后再实施 P1，要求 backlog 对全部有效输入具备可验证的新鲜度，并完成至少一次真实用户 decision。
- P2 先复用 clarifications、返工和恢复事实；只有真实 runner 消费者存在时才采集 token、耗时和工具调用。
- P3 不删除原始 occurrence，只在派生查询层降低 burst 消费成本并记录 resolution。
