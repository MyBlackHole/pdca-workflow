---
schema: pdca.asset/v1
id: ontology:domain/backup-crypto
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/backup-crypto/1.0.0
summary: backup-crypto 领域知识根节点（由 ontology/domain/backup-crypto/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件备份、加密相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# backup-crypto（领域知识根节点）

由 ontology/domain/ 迁移而来，作为该领域在本体中的分组与分类根（可被 `domain` 属性引用）。

## 子主题（已迁移为叶节点）
- `gm-support-surfaces` → `ontology:domain/backup-crypto-gm-support-surfaces`
- `medium-model` → `ontology:domain/backup-crypto-medium-model`
- `openssh-gm-support` → `ontology:domain/backup-crypto-openssh-gm-support`


## C4 组件 — backup-crypto（P1补图）

```mermaid
graph TD
    A[backup-crypto<br/>domain] --> B[core能力<br/>PDCA]
    B --> C[实现<br/>scripts/]
    %% Source: ontology/domain/backup-crypto.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/backup-crypto.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：backup-crypto 可通过本体复现
grep -q 'backup-crypto' ontology/domain/backup-crypto.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'
```

## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 门禁

- **图门禁**：`grep -c 'mermaid' ontology/domain/backup-crypto.md` ≥1
- **溯源门禁**：含 `Source:` 行号
- **校验**：`python3 scripts/ontology-validate.py` 0 issues

