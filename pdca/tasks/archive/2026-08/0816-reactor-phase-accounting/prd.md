# PRD — Reactor 相位会计专题研究

任务 ID: T0296
场景类型: research
来源: T0295（backupstream v65-v101 演进学习）识别出的深潜专题
创建: 2026-08-16

## 问题陈述

backupstream v101 引入了 Reactor 相位会计：第二套独立环形历史（`kReactorPhaseHistory=512`，
四相位 `EPOLL_WAIT/EVENT_DISPATCH/POST_DRAIN/TIMER_DISPATCH`）与 callback 历史并存，
并声称满足守恒不变量 `callback_wall + phase_wall + residual == reactor_wait`。
但该机制仅在 v101 的 ROUND101_REVIEW.md 中被描述，缺少源码级剖析与可复用方法论提炼，
其"守恒分解让不可见的忙可归因"的核心价值尚未被独立验证与文档化。

## 目标

对 Reactor 相位会计机制做源码级剖析（reactor.cpp/reactor.hpp 实现、
agent_observability.cpp server 端消费、backup_observe.cpp 离线 diagnose 消费、
ROUND100/101 文档设计意图），提炼出可跨项目复用的"事件循环时间守恒分解"方法论，
并输出实现缺口改进建议（不改码）。

## 方案

1. **实现剖析**：逐函数解析相位记录（`reactor_record_phase`）、双序列快照
   （`callback_sequence`/`phase_sequence`）、窗口重叠会计（`reactor_callback_window`，
   callback 与 phase 两套独立窗口）、top_phase/top_source 计算、守恒残差归因。
2. **消费链路剖析**：agent_observability.cpp 如何采集与暴露相位窗口；
   backup_observe.cpp 的 diagnose 如何用守恒分解归因不可见忙。
3. **方法论提炼**：将"事件循环时间守恒分解"提炼为通用方法论
   （四相位划分、双历史独立、窗口重叠会计、残差归因、截断语义）。
4. **改进建议**：基于剖析识别实现缺口或可优化点（不改码，仅建议）。

## 验收标准

- [ ] AC-1: 覆盖 v101 Reactor 相位会计的完整实现链路（reactor.cpp/reactor.hpp 记录与窗口 API、agent_observability server 端采集、backup_observe diagnose 消费）
- [ ] AC-2: 每个剖析对象给出「源码位置 + 函数级引用 + 机制说明」三要素
- [ ] AC-3: 守恒不变量 callback_wall + phase_wall + residual == reactor_wait 的推导与窗口重叠会计语义被完整说明
- [ ] AC-4: 提炼出可跨项目复用的「事件循环时间守恒分解」方法论
- [ ] AC-5: 输出实现缺口改进建议清单（含位置与理由，不改码）
- [ ] AC-6: 以源码（git show v101 diff + 当前 HEAD 文件）为事实来源，ROUND100/101 文档为设计意图佐证，并交叉核验文档与实现的一致性

## 实现/测试决策

- 无代码改动，无测试产物（research 场景）。
- 事实核验以 `git show 867da08`（v101 commit）与当前 HEAD 源码为准。
- 改进建议限于报告内陈述，不创建跟进任务（除非用户明确要求）。

## 范围外

- 不修改 backupstream 任何源码。
- 不编写独立运行验证程序（守恒不变量验证仅做静态推导）。
- 不覆盖 work_pool.cpp 中同类会计的逐行剖析（仅做关联引用）。

## 备注

- 关联 T0295 已归档，本任务为其深潜专题，parent 链可后续补充。
- 知识沉淀目标：`knowledge/linux-epoll-eventloop/` 下新增事件循环守恒分解方法论。