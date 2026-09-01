# 既有领域 composed_of 树补齐

## 背景
T0471 已为 `ontology-deep-integration` 建 5节点叶→根树（4叶1根，859 edges），但 `357 nodes` 中 `ReportCenter / Backup / TLS` 等既有领域仍为扁平 `specializes`，`ontology_tree_split` 无法调度，全库未形成可执行森林。

## 目标
为 2-3 个既有领域各补 1条最小 `composed_of` 树（1父2子，共 6 entity），保持 `validate 0 issues / islands:0`，验证模式可复制到全库。

## 范围
- 输入：`ontology/domain/report-center*`、`backup*`、`entity/tls-*` 现有节点
- 输出：6个新 `entity`（ReportCenterSystem 树 3节点 + BackupSystem 树 3节点），各 `specializes domain-entity`，`composed_of` 2子，`relates_to` 关联既有 domain 知识
- 不做：不改既有 `domain` 文件，不引入新 `domain` 类型，全库补完（留后续）

## 功能需求
1. ReportCenterSystem：`ontology:entity/report-center-system` composed_of `[report-web-subsys, collection-subsys]`（新建 2叶 entity），`relates_to` 关联 `ontology:domain/report-center`
2. BackupSystem：`ontology:entity/backup-system` composed_of `[backup-xtrabackup-entity, backup-crypto-entity]`（新建 2叶），`relates_to` 关联 `ontology:domain/backup`
3. TLS 深度：若需，补 `ontology:entity/tls-system` composed_of `[tls-session, tls-test-harness]`（复用已有 2 entity），否则跳过
4. 保持 `COMPOSED_OF_RANGE` 仅 `entity/concept`，`islands:0`

## 非功能
- 单任务引用本体数 ≤3，扇出非串联
- 6节点后 `nodes:363 / edges:866+` 仍 `islands:0`

## 验收标准
- [ ] AC-1 ReportCenter 树：`report-center-system` 存在且 `composed_of` 2叶，`ontology-validate` 0 issues
- [ ] AC-2 Backup 树：`backup-system` 存在且 `composed_of` 2叶，`graph` 含 2条新 `composed_of` 边
- [ ] AC-3 森林可调度：`tree_split` 对任意新父节点可输出 `batches [[2叶],[父]]`，`frontier` valid:true

## 关联本体节点
```
ontology:entity/report-center-system
ontology:entity/report-center-web-entity
ontology:entity/report-center-collection-entity
ontology:entity/backup-system
ontology:entity/backup-xtrabackup-entity
ontology:entity/backup-crypto-entity
ontology:domain/report-center
ontology:domain/backup
ontology:entity/tls-session
```

## 拆分映射
- ReportCenter 树 -> ontology:entity/report-center-system
- Backup 树 -> ontology:entity/backup-system
- 森林可调度 -> ontology:entity/backup-system
