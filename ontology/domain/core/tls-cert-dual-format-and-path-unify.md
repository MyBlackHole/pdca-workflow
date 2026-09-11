---
schema: pdca.asset/v2
id: ontology:domain/tls-cert-dual-format-and-path-unify
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/tls-cert-dual-format-and-path-unify/3.1.0
summary: cert-dual-format-and-path-unify
domain:
- ontology:domain/tls
relations:
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/tls
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 运行 grep -q 'cert-dual-format-and-path-unify' ontology/domain/core/tls-cert-dual-format-and-path-unify.md；文本命中仅证明描述存在，领域行为需另行验证。
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
title: ED25519 双格式回退与证书路径统一
source: records/T0342-0822-tls-cert-init-api/conclusion.md
---

## 复用规则

- 证书文件名以 `common.h` 为唯一常量源：`CERT_FILE_ED25519_*`（新有前缀）与 `CERT_FILE_*`（旧无前缀）并存，注释“新优先旧回退”；`tls_cert` 与 `tls_keygen` 均 `include "common.h"` 后复用，禁止各自 `snprintf("%s_host.key", algo)` 硬编码。
- `ED25519` 加载时有前缀优先回退无前缀：`slot_create` 对 `ca/cert/key` 三文件依次 `stat` 探测，`ed25519_*` 存在即用，否则回退 `ca.crt/host.crt`，`SM2` 单格式 `sm2_*` 不回退。
- `ca_cn` 仅允许 `[A-Za-z0-9._-]` 且禁 `..`，含 `/` 直接 `INVALID_PARAM`，防路径遍历。

## 适用边界

- 仅 `cert_dir` 驱动的 `tls_cert` 初始化，不兼容旧 `profiles` 手填与 `server/client` 前缀文件。
- 热重载/轮转不在本知识。

## 来源

- `records/T0342-0822-tls-cert-init-api/conclusion.md`
- `records/T0342-0822-tls-cert-init-api/evidence/test_tls_cert_v2.log`
