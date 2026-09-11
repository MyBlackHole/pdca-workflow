---
schema: pdca.asset/v2
id: ontology:domain/skill-build-config
name: build-config
summary: Set up build configuration for new projects, manage dependencies, and switch between build systems.
description: Use when setting up build configuration for new projects, adding/managing dependencies, or switching
  between C/C++/Rust/Go/Python build systems
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/skill-build-config/3.1.0
relations:
  relates_to:
  - ontology:concept/design-tree
  - ontology:concept/domain-model
  - ontology:concept/pdca-task
  instance_of:
  - ontology:concept/knowledge-artifact
revision: 3.1.0
authority: reference
validation:
  structural_checks:
  - 递归解析本节点身份及关系列表；目标 ID 必须可定位。引用数量不作为行为验证。
  claim_status: unverified
  adoption: claim_review_required
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
---

-----|------|
| C/C++ (GCC) | `-fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wl,-z,now` |
| C/C++ (Clang) | `-fsanitize=address,undefined` |
| Rust | 默认安全（unsafe 例外） |
| Go | 默认 W^X |

## 已知坑

- 依赖版本勿随意跳大版本；构建系统切换须保持全仓一致，混用会引入不可复现构建。
