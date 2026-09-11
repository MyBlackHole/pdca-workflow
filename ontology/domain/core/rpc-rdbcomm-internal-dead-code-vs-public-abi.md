---
schema: pdca.asset/v2
id: ontology:domain/rpc-rdbcomm-internal-dead-code-vs-public-abi
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/rpc-rdbcomm-internal-dead-code-vs-public-abi/3.1.0
summary: internal-dead-code-vs-public-abi
domain:
- ontology:domain/rpc-rdbcomm
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/rpc-rdbcomm
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 运行 grep -q 'internal-dead-code-vs-public-abi' ontology/domain/core/rpc-rdbcomm-internal-dead-code-vs-public-abi.md；文本命中仅证明描述存在，领域行为需另行验证。
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

---
schema: pdca.ontology/domain/v1
title: 清理网络遗留代码时区分内部死代码与公共 ABI
source: records/T0316-0818-rpc-legacy-helper-cleanup/conclusion.md
---

## 可复用规则

发现未使用函数时，应先按链接边界分类：静态内部函数若无仓库内调用，可在构建和完整测试保护下删除；公共头文件中的无内部调用函数不能仅凭源码搜索删除，应保留并单独评估外部 ABI。

编译器的 `unused` 属性也要区分：实际有调用的函数只需移除错误属性；属性本身不是删除函数的证据。网络收发辅助函数还必须确认其帧格式和 I/O 所有权，不能把旧原始 fd 实现误删为当前 TLS session 实现。

## 来源

T0316 对 `rpc-net`、`tls-keygen` 和 TLS 公共 API 的分类审查，以及 36 项完整测试结果。
