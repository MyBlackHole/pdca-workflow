---
schema: pdca.asset/v1
id: T0296-0816-reactor-phase-accounting
phase: check
source_ids: [reactor-phase-accounting-report-v3, convergence-map-v3]
---

## 上下文

T0296（research 场景）是 T0295 深潜专题：对 backupstream v101（commit 867da08）的
Reactor 相位会计机制做源码级剖析。研究对象包括 reactor.cpp/reactor.hpp（记录与窗口 API）、
work_pool.cpp/hpp（producer 双序列快照）、agent_observability.cpp（server 端采集归因）、
backup_observe.cpp（离线 diagnose 消费）、ROUND101_REVIEW.md（设计意图）。
交付物为报告 + 知识沉淀 + 改进建议（不改码），产出存 PDCA records。

## 假设与结果

| 假设 | 结果 | 结论 |
|------|------|------|
| v101 相位会计机制可完整链路剖析 | 四段链路（producer 快照→记录→窗口→归因/诊断）全部核验 | 满足 AC-1/AC-2 |
| 守恒不变量 callback+phase+residual==wait 成立 | 会计域不相交设计 + server 残差公式 + 集成测试 b-21-1 数值验证成立 | 满足 AC-3 |
| 可提炼跨项目方法论 | 提炼「事件循环时间守恒分解」5 条原则 | 满足 AC-4 |
| 存在实现缺口 | 输出 5 条改进建议（含位置与理由） | 满足 AC-5 |
| 文档与实现一致 | 9 项交叉核验全部一致（守恒/域不相交/truncated/容量512/互不挤占/回退） | 满足 AC-6 |

## 分析

**核心机制**：v101 增加第二套独立固定容量（512）相位环形历史，与 256 条目 callback
历史并存。四相位（epoll-wait/event-dispatch/post-drain/timer-dispatch）区间刻意记录在
leaf callback 体之外（dispatch 前/回调后分别埋点），使会计域两两不相交——这是守恒
等式成立的前提。producer 在 work completion 入队时经 observation 快照双序列游标
（callback_sequence/phase_sequence），consumer 在运行回调时用 `reactor_callback_window`
在 [enqueued, run] 区间做重叠裁剪会计。server 端输出
`reactor_residual_ns = reactor_wait_ns - callback_wall_ns - phase_wall_ns`
（仅两 history complete 且减法非负）。离线 diagnose 产生三类 confirmed finding：
`reactor-phase-history-truncated`（环回绕拒绝归因）/
`reactor-internal-phase-busy`（归因到相位）/`reactor-residual-delay`（归因到域外）。

**修正补充（grill 判定"需补充深入"+"缺少架构图"）**：① 补充 work_pool producer 端
深入剖析（work_pool.cpp:376-402）——observation 捕获仅当 `item->lifecycle` 存在时走
观察版 `reactor_post_wait_priority_observed_kind`，否则无会计；observation 三字段
（enqueued_ns/callback_sequence/phase_sequence）为 post 入队瞬间 acquire 游标；
post 失败时 observation 不采纳且 completion_pending 复位；三字段在初始与复用前归零。
② 补充「链路架构总览」ASCII 图（producer→记录→窗口→归因→诊断 五段 + 守恒等式），
置于报告发现部分第 0 节。报告重登记为 v3，收敛映射 v2，validate-convergence valid:true。

## 适用边界

- 结论限于 v101（867da08）与当前 HEAD 状态；未来版本需重新核验。
- `reactor_wait_ns` 仅覆盖 completion enqueue→run 区间，不覆盖 work 执行本身。
- 相位历史 512 固定容量，超高事件率下可能频繁 truncated（届时仅产生
  `phase-history-truncated`，不产生相位/残差归因）。
- `epoll-wait` 相位含线程去调度时间，不能直接解读为 epoll 问题。
- 改进建议仅在报告陈述，不改码、不建跟进任务（用户已确认）。

## AC 判定

- **AC-1** ✓：完整实现链路覆盖（reactor 记录/窗口、work_pool producer、agent_observability server、backup_observe diagnose）。
- **AC-2** ✓：每个剖析对象含「源码位置+函数级引用+机制说明」。
- **AC-3** ✓：守恒不变量推导与会计域不相交语义（含集成测试数值验证）。
- **AC-4** ✓：「事件循环时间守恒分解」方法论 5 条原则。
- **AC-5** ✓：5 条改进建议（含位置与理由，不改码）。
- **AC-6** ✓：git diff + 当前 HEAD 为事实来源，ROUND101 佐证，9 项交叉核验一致。

## 下一轮建议

- 若 `reactor-internal-phase-busy` 反复指向单相位，按 ROUND101 预告将该相位拆分为
  若干编译期子相位，并为本相位补充 cpu_ns（对应改进建议 #3）。
- 若 `reactor-residual-delay` 反复显著，下一轮增加保守的 scheduler/run-state 证据
  （对应改进建议 #5）。
- 可将「事件循环时间守恒分解」方法论沉淀到 knowledge/linux-epoll-eventloop/。

## 结论

verdict = **confirmed**（待用户确认）