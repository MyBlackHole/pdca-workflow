# system增zfs-zil至8叶全栈完成100% Rule

## 背景
`T0526` 已使 `zfs-system` 7叶含 `vdev`，`T0527` 已新建 `zfs-zil` 独立实体但尚未纳入 `system`，当前 `composed_of` 7叶仍缺 `zil` 维度，`gate --check hundred` 虽 `PASS`（7叶覆盖100% keys）但未100%全栈。需增 `zil` 至8叶完成 `ZPL→DMU→DSL→SPA→ZIO→VDEV→ZIL横切ARC` 全栈。

## 目标
- `ontology/entity/zfs-system.md` `composed_of` 增 `ontology:entity/zfs-zil` 至8叶，`summary` 更新为8叶
- `attributes.seven_leaf_completeness` 更名为 `eight_leaf_completeness` 且约束更新为8叶，`testable_signal` `ls | wc -l | awk >=9`（8叶+1系统=9文件）
- `gate --check hundred --node zfs-system` 仍 `PASS` 且 `grep -q zfs-zil` 命中

## 范围
- 输入：`zfs-system.md:150行` 7叶 + `zfs-zil.md:168行`
- 输出：`zfs-system.md` 8叶 + `validate 0` + `gate PASS`
- 不做：不改其他叶

## 功能需求
1. `composed_of` 增 `zfs-zil`，`relates_to` 已含 `production-ontology-scientific-gate` 保持
2. `summary` 更新为8叶，`attributes` 约束更新为8叶，`testable_signal` 更新 `wc -l >=9`
3. `gate --check hundred --node zfs-system` `coverage 100%` 仍 PASS

## 非功能需求
- 中文；`validate 0` `islands:0`

## 验收标准
- [ ] AC-1 composed_of：`grep -q 'zfs-zil' ontology/entity/zfs-system.md` PASS
- [ ] AC-2 hundred：`gate --check hundred --node zfs-system` PASS
- [ ] AC-3 全绿：`validate 0` + `scaffold`可产
- [ ] AC-4 收敛 valid:true

## 关联本体节点
```
ontology:entity/zfs-system
ontology:entity/zfs-zil
```

## 拆分映射
- 增zil -> relations
