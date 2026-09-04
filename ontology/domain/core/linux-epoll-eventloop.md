---
schema: pdca.asset/v1
id: ontology:domain/linux-epoll-eventloop
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/linux-epoll-eventloop/1.0.0
summary: linux-epoll-eventloop 领域知识根节点（由 ontology/domain/linux-epoll-eventloop/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件Linux相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# linux-epoll-eventloop（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `backupstream-v65-v101-arch-evolution` → `ontology:domain/linux-epoll-eventloop-backupstream-v65-v101-arch-evolution`
- `dynamic-deadline-wakeup` → `ontology:domain/linux-epoll-eventloop-dynamic-deadline-wakeup`
- `event-loop-time-conservation` → `ontology:domain/linux-epoll-eventloop-event-loop-time-conservation`
- `multireactor-so-reuseport` → `ontology:domain/linux-epoll-eventloop-multireactor-so-reuseport`
- `rpc-conn-idle-reclaim` → `ontology:domain/linux-epoll-eventloop-rpc-conn-idle-reclaim`
- `transport-ownership-model` → `ontology:domain/linux-epoll-eventloop-transport-ownership-model`
