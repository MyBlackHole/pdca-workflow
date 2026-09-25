---
schema: pdca.asset/v2
id: ontology:process/flow-plan
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.3
dcterms_modified: '2026-09-25'
summary: Plan：与你确认问题，再形成计划
---

# Plan：与你确认问题，再形成计划

## 进入前

本任务独立 Agent 已绑定；用户看到当前 Plan 目标并作匹配 `phase_start` 操作。
先确认问题、范围/非目标、预期交付及约束；已有明确答案引用，不重复盘问。
未批准时只沟通，不建本体、不改业务文件。

## 本阶段自主执行

读取当前 SCENE 方法与固定来源，区分事实、假设和未知。寻找可复用模型，确认版本及限制；
确定本节点职责、直接子 seed 或 leaf 理由。提出方案、实质取舍、可独立验收的产物、
AC/oracle、测试/反例、写域和停止条件。

计划覆盖真实本体源或对应场景对象，不允许把任务名称当交付证明。
发现目标含糊先问具体决策问题，事实性问题由 Agent 自查；不要把“知识地图”替代正式模型。

正式分解必须从当前固定 ontology/work instance 出发：
- 先定位具名 ontology object/work instance、与当前节点的语义关系及适用 constraint；
- 只有该候选同时满足 NODE-01 的独立职责、固定 I/O、可独立拒收成果和验证边界，才生成正式 child seed；
- seed 必须记录来源 ontology revision、node/relation、dependency、组合责任和 CONTEXT-01 上下文边界；
- 是否创建由用户工作级操作决定，Plan 不能直接 spawn。

如果只是当前 Do 的机械执行切片，使用 [CONTRACT-01](../concept/pdca-execution-contract.md)
的 Do-only Work Unit，不创建 node/task/Agent。

不使用 LOC、预计工时、模块数量、token、并行度或 Agent 置信度作为正式拆分依据。

## 完成与等待

保存 plan、基线、输入清单和必要模型 seed，标记 `phase_completed`。
向用户报告计划以及下一 Do 的固定对象、写域和限制，然后停止。

Do 的 `phase_start` 必须来自 Plan `phase_completed` **之后的新用户操作**。
Plan 期间的预批准、最初“开始”、future blanket approval，或“如果 Plan 通过就继续”
都不能启动 Do。
