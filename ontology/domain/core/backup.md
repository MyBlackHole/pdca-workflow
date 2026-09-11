---
schema: pdca.asset/v2
id: ontology:domain/backup
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/backup/3.1.0
summary: backup 领域知识根节点（由 ontology/domain/backup/ 迁移）
relations:
  relates_to:
  - ontology:concept/pdca
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

# backup（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `gs-roach-gm-encrypt-support` → `ontology:domain/backup-gs-roach-gm-encrypt-support`
- `ob-backup-gm-encrypt-support` → `ontology:domain/backup-ob-backup-gm-encrypt-support`
- `xtrabackup-incremental-schemes` → `ontology:domain/backup-xtrabackup-incremental-schemes`


## C4 组件 — backup（P1补图）

```mermaid
graph TD
    A[backup<br/>domain] --> B[core能力<br/>PDCA]
    B --> C[实现<br/>契约产物]
    %% Source: ontology/domain/core/backup.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/core/backup.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：backup 可通过本体复现
```

结构审查使用 ontology:concept/ontology-creation-gate；旧工作流命令已移除。
## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 使用与验证边界

结构审查按 ontology:concept/ontology-creation-gate。正文中的领域断言需在授权的实际源码版本中核对；原历史路径和记录不是当前任务已执行证据。图表、行数或测试骨架数量不作为默认通过条件。
