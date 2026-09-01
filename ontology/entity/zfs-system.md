---
schema: pdca.asset/v1
id: ontology:entity/zfs-system
type: entity
layer: Knowledge
status: active
summary: ZFS 全栈系统聚合（composed_of DMU/DSL/SPA/ZIO/ZPL/ARC 六叶，C4 L2/L3 至 ZIO pipeline 可建模）
relations:
  specializes:
    - ontology:concept/domain-entity
  composed_of:
    - ontology:entity/zfs-dmu
    - ontology:entity/zfs-dsl
    - ontology:entity/zfs-spa
    - ontology:entity/zfs-zio
    - ontology:entity/zfs-zpl
    - ontology:entity/zfs-arc
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/scientific-research-methodology
    - ontology:domain/zfs-crypto
attributes:
  - name: c4_l2_coverage
    desc: C4 L2 全栈容器覆盖
    constraint: 覆盖 ZPL→DMU→DSL→SPA→ZIO→VDEV 横切 ARC/ZIL 的容器图且 mermaid 可渲染
    testable_signal: "运行 grep -q 'C4 L2' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -c '```mermaid' records/T0503-0903-research-zfs-implementation/research-report.md | awk '{exit !($1>=6)}'"
  - name: zio_pipeline_depth
    desc: ZIO pipeline 下钻至 L3 可测
    constraint: 下钻至 ZIO stage 位图与 pipeline 宏，含 compress/encrypt/checksum/dedup 分支
    testable_signal: "运行 grep -q 'ZIO.*PIPELINE' records/T0503-0903-research-zfs-implementation/research-report.md 且 grep -q 'ZIO_STAGE_VDEV_IO_START' include/sys/zio_impl.h 命中"
  - name: six_leaf_completeness
    desc: 六叶 composed_of 完整性
    constraint: composed_of 恰为 dmu/dsl/spa/zio/zpl/arc 六叶且可 scaffold
    testable_signal: "运行 python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0' 且 ls ontology/entity/zfs-*.md | wc -l | grep -q '7'"
---

# ZFS 全栈系统（ZFS System）

OpenZFS 实现全栈的系统聚合，`composed_of` 六叶 `zfs-dmu`/`zfs-dsl`/`zfs-spa`/`zfs-zio`/`zfs-zpl`/`zfs-arc`，以 `research-diagram-methodology` 6 图 `mermaid` 为可视化证据（C4 L2 全栈 + ZIO pipeline 时序 + DMU 逻辑 + TXG 状态机 + 数据流 + C4 L1 上下文），每图附 `Source: file:line` 直达 `openzfs/zfs#master`。

验证：`grep -c '```mermaid' records/T0503-0903-research-zfs-implementation/research-report.md` ≥6 且 `python3 scripts/ontology-validate.py` 0 issue 且 `islands:0`。

Source: `records/T0503-0903-research-zfs-implementation/research-report.md`（6 图全覆盖）+ `openzfs/zfs/include/sys/zio_impl.h:60-260`
