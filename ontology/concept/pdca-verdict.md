---
schema: pdca.asset/v2
id: ontology:concept/pdca-verdict
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: VERDICT-01：执行完成、对象符合和工作完成分离
---

# VERDICT-01：执行完成、对象符合和工作完成分离

每个AC使用pass/fail/unknown/not_run并说明来源；结论区分task_execution、subject_conformance、delivery_usable和场景覆盖。多数PASS不能覆盖必需fail／unknown；自定义较窄套件不能删除SCENE要求的真实本体源。

正确发现不符合的审查任务可以完成，但被审对象仍不符合。用户可批准Act仅失败归档，不自动使delivery_usable=true；风险接受需具体对象与限制，不伪造测试PASS。

modeling本地完成、整树冻结、projection实现可用、verification通过、发布已授权是不同事实。场景未运行保持not_run；不能以一个task=archive宣布整个工作完成。

全工作通过需固定节点集合、所有必需三场景任务的真实覆盖、目标和组合符合、无阻断未知，且发布／使用范围得到明确处置。阶段结束只是等待下一次操作，不自动生成后继。
