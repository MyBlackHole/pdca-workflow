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

## 方法边界

phase_start 的用户授权、Gate、started receipt 与 running 状态由 CONFIRM-01 / GATE-01 /
TRANSITION-01 / STATE-01 统一处理。本页只定义 **Plan run 已开始之后** 的计划方法。

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

## 结果包

Plan 方法产出固定 plan、baseline、输入清单、AC/oracle、写域/资源边界和必要 seed。
这些结果交给 TRANSITION-01 作为本 run 的 `phase_completed` 依据；下一 Do 的授权不由本页生成。
