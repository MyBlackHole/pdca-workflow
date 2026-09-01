# 业务三演练：Report Collection 域

## 背景
T0479/T0480 已验证 Report Web / Backup Xtrabackup 单叶演练，Report Collection 同为 `report-center-system` 第二叶，需第三单验证第二叶同可调度。

## 目标
以 `collection` 叶为第三演练，产出可复用模板第三例。

## 功能需求
1. `Collection Demo -> ontology:entity/report-center-collection-entity`，tree_split 单叶
2. 为 `report-center-collection-entity` 补 `attributes.demo_collection` + scaffold
3. 桩 `collection/src/demo.py` 返回 `{"collection":1}`

## 验收标准
- [ ] AC-1 拆分可调度
- [ ] AC-2 本体测试通过
- [ ] AC-3 桩可验证且全绿

## 关联本体节点
```
ontology:entity/report-center-system
ontology:entity/report-center-collection-entity
```

## 拆分映射
- Collection Demo -> ontology:entity/report-center-collection-entity
