---
schema: pdca.asset/v1
id: T0512-0906-study-sixlock
phase: check
source_ids: [report-sixlock, convergence-map]
---

## 上下文
20 轮新规划第 11 轮（实质调研第一轮）。SIX 锁专题学习报告模式：主会话精读源码，对话全文 + 报告文件。

## 假设与结果
- 假设 1：six.h DOC 足够支撑学习。结果：成立，124 行 DOC 加实现抽查。
- 假设 2：research 豁免合规。结果：成立，学习报告不产本体，ontology_exempt=true。

## 分析
- **AC-1** ✅ 九节覆盖三态/升降级/死锁/性能，每节有 file:line 锚点（report-sixlock）
- **AC-2** ✅ 报告文件存在，对话全文待本回复交付后成立（report-sixlock）
- **AC-3** ✅ 每节收束设计启示，第九节汇总七条（report-sixlock）

关键结论：SIX 锁七条设计启示；最重要的是错配量化、零分配快路、seq 版本化、定向唤醒、原语策略分离。
复核途径：按报告复核途径节定位源码。

## 适用边界
- 基于当前 main 快照；six.c/locking.c 实现细节以抽查为准，未逐行审计。

## 下一轮建议
- 按新规划进入第 12 轮：journal 崩溃恢复专题。

verdict: {"outcome": "confirmed", "reason": "3 AC 全绿，九节学习报告有锚点有启示", "verdict_id": "vt0512-confirmed", "at": "2026-09-06T00:00:00+08:00"}

## 本体沉淀

决策：`ontology:ontology:domain/core-sixlock-study-guide`（T0513 新流程下补建）。

理由：SIX 锁学习报告含七条设计启示，属可复用清单；锁主题已有 7 个机制节点，本次新建学习指南节点做导航聚合，不重复机制内容。来源 record `T0512-0906-study-sixlock`。
