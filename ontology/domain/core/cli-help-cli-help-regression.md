---
schema: pdca.asset/v2
id: ontology:domain/cli-help-cli-help-regression
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/cli-help-cli-help-regression/3.1.0
summary: CLI help 完整性与回归规范
domain:
- ontology:domain/cli-help
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/cli-help
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 运行 grep -q 'cli-help' ontology/domain/core/cli-help-cli-help-regression.md；文本命中仅证明描述存在，领域行为需另行验证。
  verification_level: structural
  evidence_level: structure
revision: 3.1.0
authority: reference
semantic_kind: individual
validation:
  structural_checks:
  - ontology:concept/ontology-creation-gate
  claim_status: unverified
  adoption: claim_review_required
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

# CLI help 完整性与回归规范

## 适用范围

适用于仓库内用户可见命令行工具及其子命令。

## 规则

1. 新增或修改 CLI 参数时，必须同步更新 `--help`：说明作用、是否需要值、默认值或取值约束，以及与其他参数的关系。
2. 每个工具至少提供一个可复制的使用案例；涉及服务、证书或文件时必须注明前置条件。
3. help 案例默认只展示命令文本，不在 help 回归测试中启动服务、生成证书、覆盖用户文件或执行其他副作用操作。
4. 参数注册表、解析逻辑和 help 文本必须保持一致；声明为带值参数的选项必须由解析器按带值参数处理。
5. 回归测试应直接执行构建后的工具和子命令 help，断言参数、案例标题和关键约束，而不是只检查源代码字符串。

## 来源

本规范由 T0318 `补充工具 help 参数说明与使用案例` 沉淀，证据见对应任务记录。
