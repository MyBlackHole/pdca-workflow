# ZFS全栈实体叶→根实现：zfs-system 6叶开发

## 背景

T0503已全栈调研 `zfs-system composed_of 6叶`（dmu/dsl/spa/zio/zpl/arc）各叶 `attributes.testable_signal` 可 `scaffold`，T0501多图模板已验证。需按 `hybrid-develop-bottomup` 叶→根实现，叶 `dependencies:[]` 并行，根聚叶。

## 目标

- 6叶各产 `ontology/entity/zfs-*` 对应实现桩+ `scaffold` 3模式验证
- `zfs-system` 聚合验证 `tree_split` 可调度且 `ready-set [[6叶],[system]]`

## 范围

- 输入：`ontology/entity/zfs-system.md` 6 `composed_of` + `scientific-research-methodology`
- 输出：6叶实现桩 + 1系统聚合 + 全绿
- 不做：不改ZFS源码，仅桩接口与本体对齐

## 功能需求

1. 叶实现：zfs-dmu/dsl/spa/zio/zpl/arc 各1桩（`interface+test` 通过 `testable_signal` 三模式）
2. 根聚合：`zfs-system` 依赖6叶，`compute-frontier` 可算 `batches [[6叶],[system]]`
3. 门禁：`validate 0 + islands:0 + scaffold 6叶可产 + convergence valid`

## 非功能需求

- 叶并行根串行，可分配至1人1验

## 验收标准

- [ ] AC-1 6叶实现：各叶桩+test可 `pytest --collect-only` 命中
- [ ] AC-2 根聚合：`zfs-system` `composed_of 6叶` 且 `tree_split` 可调度
- [ ] AC-3 叶→根：`ready-set [[6叶],[system]]` `valid:true`
- [ ] AC-4 全绿 `islands:0` `scaffold 6叶可产`
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:entity/zfs-system
ontology:entity/zfs-dmu
ontology:entity/zfs-dsl
ontology:entity/zfs-spa
ontology:entity/zfs-zio
ontology:entity/zfs-zpl
ontology:entity/zfs-arc
ontology:domain/ontology-hybrid-develop-bottomup
```

## 拆分映射

- DMU -> ontology:entity/zfs-dmu
- DSL -> ontology:entity/zfs-dsl
- SPA -> ontology:entity/zfs-spa
- ZIO -> ontology:entity/zfs-zio
- ZPL -> ontology:entity/zfs-zpl
- ARC -> ontology:entity/zfs-arc
- System聚合 -> ontology:entity/zfs-system
