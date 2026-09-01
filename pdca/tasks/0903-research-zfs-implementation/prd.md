# 调研ZFS实现：DMU/DSL/SPA/ZIO/ZPL全栈与OpenZFS

## 背景

OpenZFS全栈（ZPL→DMU→DSL→SPA→ZIO→ARC）缺乏架构师可一图建模的研究，T0500类ZFS Crypto即因缺 `C4 L2` + `ZIO pipeline` + `TXG状态机` 难理解。需按 `scientific-research-methodology` 四支与 `research-diagram-methodology` 多图模板，以 `openzfs/zfs` GitHub primary source 全栈调研，产出多图研究报 + 本体树 `zfs-system composed_of`。

## 目标

- 产出 `research-report.md` 含P0必含 `C4 L2` 架构图 + `ZIO pipeline` 数据流 + `DMU` 逻辑时序，P1 `TXG生命周期状态机` + `C4 L1` 上下文，6图 `mermaid` inline，每图1条 `Source: openzfs/zfs file:line` 引证
- 沉淀 `ontology/entity/zfs-system(composed_of: dmu, dsl, spa, zio, zpl, arc)` 6叶实体，各叶 `attributes.testable_signal` 可 `scaffold`

## 范围

- 输入：`openzfs/zfs` GitHub + 官方doc + `C4 L2/L3`（`L2 Container`至 `ZIO pipeline` L3 Component）
- 输出：1 report（含6图） + 6 entity + 1 system 聚合 + 全绿
- 不做：不改ZFS代码，不深至 `dbuf` L4 Code

## 功能需求

1. 全栈概览：`C4 L2` Container（ZPL→DMU→DSL→SPA→ZIO→VDEV）+ `C4 L3` Component至 `ZIO pipeline`（`zio_create→zio_execute→vdev_queue`）
2. DMU/SPA深度：DMU `dnode/dbuf` 逻辑时序 + SPA `TXG` 状态机（`open→quiescing→syncing→open`）
3. Primary source可验证：每图 `Source: openzfs/zfs/module/...:line` + `openzfs docs` 链接
4. 本体沉淀：6叶 `zfs-dmu/dsl/spa/zio/zpl/arc` + `zfs-system` 聚合，`islands:0`，`relates_to` 可 `graph` 追
5. 门禁：`grep -c mermaid ≥3` 且 `grep -c Source: ≥3` + `validate 0`

## 非功能需求

- 架构师一图可建模，`mermaid` 可渲染，`Source` 可点击至 `GitHub file:line`

## 验收标准

- [ ] AC-1 报告多图：`research-report.md` 含6图 `mermaid` ≥3（P0 `C4 L2`+`ZIO pipeline` 必含）且每图含 `Source:`
- [ ] AC-2 本体树：`zfs-system` 6叶 `composed_of` 且各叶 `attributes` 可 `scaffold` 且 `validate` 通过
- [ ] AC-3 深度：`C4 L2+L3` 至 `ZIO pipeline` + `DMU` 时序 + `SPA TXG` 可 `grep` 命中
- [ ] AC-4 本体沉淀：6叶+1系统已 `ontology/entity` 落盘且 `disposition ontology:` 回链
- [ ] AC-5 全绿：`islands:0` 且 `validate-convergence valid:true`

## 关联本体节点

```
ontology:entity/zfs-system
ontology:entity/zfs-dmu
ontology:entity/zfs-dsl
ontology:entity/zfs-spa
ontology:entity/zfs-zio
ontology:entity/zfs-zpl
ontology:entity/zfs-arc
ontology:pattern/scientific-research-methodology
ontology:pattern/research-diagram-methodology
```

## 拆分映射

- 架构图C4 L2/L3 -> ontology:entity/zfs-system
- ZIO pipeline -> ontology:entity/zfs-zio
- DMU深度 -> ontology:entity/zfs-dmu
- SPA/TXG -> ontology:entity/zfs-spa
- DSL/ZPL/ARC -> ontology:entity/zfs-dsl
