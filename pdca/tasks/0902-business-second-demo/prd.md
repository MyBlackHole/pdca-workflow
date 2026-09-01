# 业务二演练：Backup 域

## 背景
T0479 已验证 ReportCenter 新路径首单，Backup 域 `backup-system` 树（T0477）同为 1父2子，需第二业务单验证可复制性。

## 目标
以 Backup 域为第二演练，复用 `拆分映射→scaffold→桩→convergence` 四步，产出可复制模板。

## 功能需求
1. `Demo -> ontology:entity/backup-xtrabackup-entity`，`tree_split` 单叶验证
2. 为 `backup-xtrabackup-entity` 补 `attributes.demo_backup` + scaffold
3. 桩 `backup/src/demo.py` 返回 `{"backup":1}` + 测试

## 验收标准
- [ ] AC-1 拆分可调度：tree_split 对 Backup 叶 valid
- [ ] AC-2 本体测试：scaffold 对 backup-xtrabackup 通过
- [ ] AC-3 桩可验证：demo 桩 `{"backup":1}` ผ่าน 且全绿

## 关联本体节点
```
ontology:entity/backup-system
ontology:entity/backup-xtrabackup-entity
```

## 拆分映射
- Backup Demo -> ontology:entity/backup-xtrabackup-entity
