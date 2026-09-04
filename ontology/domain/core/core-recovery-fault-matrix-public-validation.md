---
schema: pdca.asset/v1
id: ontology:domain/core-recovery-fault-matrix-public-validation
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-recovery-fault-matrix-public-validation/1.0.0
summary: Recovery fault matrix and public derived validation
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 recovery-fault-matrix-public-validation 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# Recovery fault matrix and public derived validation

在 journal replay → derived rebuild → publication 的 recovery 顺序中，派生状态校验必须保持
只读，并可通过公开 API 独立调用。fault 注入应绑定三个边界：replay 后、rebuild 阶段、publication
前；任一 fault 都不得返回成功恢复对象。结构化 mismatch 至少区分 invalid pointer、generation、
duplicate backpointer、alloc set 和 backpointer set，便于测试和上层诊断。
