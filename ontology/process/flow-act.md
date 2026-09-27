---
schema: pdca.asset/v2
id: ontology:process/flow-act
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-14'
summary: Act：执行用户批准的处置，然后停止
---

# Act：执行用户批准的处置，然后停止

## 方法边界

Act 的用户授权、Check predecessor、处置 subject freshness、started receipt 与 running 状态由
CONFIRM-01 / GATE-01 / TRANSITION-01 / STATE-01 处理。本页只定义 **Act run 已开始之后** 的处置方法。

## 本阶段自主执行

按批准范围固定交付、结果与限制；已授权发布才发布，并核查实际结果。经验保留来源版本、环境、反证、适用范围和重评条件；没有新知识就none，不强造内容。停止业务操作并结清或明确隔离资源。

验收fail／unknown可以在用户批准下诚实归档，但delivery_usable保持相应限制。一次建模任务不代表整树或三场景完成。未来场景没有运行就not_run。

## 结果包

固定最终交付、处置证据、资源归还/retained 隔离依据和实际 scene coverage。
这些结果先作为 Act `phase_completed` 依据；已授权终态处置确实完成后，TRANSITION-01 再记录 `archived`。
归档不是第五阶段，也不产生下一 task/scene/attempt 的授权。
