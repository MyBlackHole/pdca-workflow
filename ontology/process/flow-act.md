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
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: Act：执行用户批准的处置，然后停止
---

# Act：执行用户批准的处置，然后停止

## 进入前

用户明确批准Act具体范围，引用当前Check报告和对应产物；说明仅归档、接受交付、返工安排、局部经验或共享发布。一个模糊“好”不能被扩大成全局知识更新。

## 本阶段自主执行

按批准范围固定交付、结果与限制；已授权发布才发布，并核查实际结果。经验保留来源版本、环境、反证、适用范围和重评条件；没有新知识就none，不强造内容。停止业务操作并结清或明确隔离资源。

验收fail／unknown可以在用户批准下诚实归档，但delivery_usable保持相应限制。一次建模任务不代表整树或三场景完成。未来场景没有运行就not_run。

## 完成

固定phase_completed、archived记录与最终task索引，发布归还回执。归档是本次Act处置的一部分，不新增第五阶段。报告实际结果与尚未启动的建议，停止；不自动新建任务、继续projection／verification或开启下一attempt。
