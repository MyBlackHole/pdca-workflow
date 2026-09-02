---
schema: pdca.asset/v1
id: ontology:domain/backup
type: domain
layer: Knowledge
status: active
summary: backup 领域知识根节点（由 ontology/domain/backup/ 迁移）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca
  testable_signal: "检查本文件备份相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

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
    B --> C[实现<br/>scripts/]
    %% Source: ontology/domain/backup.md:1 + ontology/concept/ontology-fidelity-criterion.md:1
```

Source: `ontology/domain/backup.md:1` + `ontology/concept/ontology-fidelity-criterion.md:1`

## 正例

```bash
# 正例：backup 可通过本体复现
grep -q 'backup' ontology/domain/backup.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'
```

## 反例

```bash
# 反例：缺图导致不可视化
# 无 mermaid 时，AI无法从本体还原组件关系，需补图
```

## 门禁

- **图门禁**：`grep -c 'mermaid' ontology/domain/backup.md` ≥1
- **溯源门禁**：含 `Source:` 行号
- **校验**：`python3 scripts/ontology-validate.py` 0 issues

