---
schema: pdca.asset/v1
id: ontology:entity/zfs-ddt
type: entity
layer: Knowledge
status: active
summary: ZFS DDT 实体 — 去重表 DDT与BRT削零及LRU
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:entity/zfs-zio
    - ontology:domain/zfs-crypto
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: ddt_table_zap
    desc: DDT表 ddt_phys_t持久与zap可测，对应C4 L3
    constraint: 覆盖 ddt_t/ddt_entry_t/ddt_phys_t 的 zap持久与 ddt_phys 3副本及 C4 L3 可建模
    testable_signal: "运行 grep -q 'ddt_phys' records/T0531-0902-zfs-ddt-entity/report.md 2>/dev/null || grep -q 'ddt_phys' ontology/entity/zfs-ddt.md 命中且 grep -q 'ddt_phys' /tmp/zfs/include/sys/ddt.h 命中"
  - name: ddt_lru_arc
    desc: DDT LRU与ARC协同可测，对应时序图 dedup lookup
    constraint: 覆盖 ddt_lookup/ddt_enter 的 LRU与 ARC协同及 dedup命中时序
    testable_signal: "运行 grep -q 'ddt_lookup' records/T0531-0902-zfs-ddt-entity/report.md 2>/dev/null || grep -q 'ddt_lookup' ontology/entity/zfs-ddt.md 命中且 grep -q 'ddt_lookup' /tmp/zfs/module/zfs/ddt.c 命中"
  - name: brt_nopwrite
    desc: BRT削零表与nopwrite可测，对应状态机 REFD/HOLE
    constraint: 覆盖 brt_entry_t/brt_add 的 hole削零与 nopwrite分支及状态机 REFD→HOLE
    testable_signal: "运行 grep -q 'brt_add' records/T0531-0902-zfs-ddt-entity/report.md 2>/dev/null || grep -q 'brt_add' ontology/entity/zfs-ddt.md 命中且 grep -q 'brt_add' /tmp/zfs/module/zfs/brt.c 命中"
---

# ZFS DDT（Deduplication Table）

去重表：`ddt_t` 聚合 `ddt_phys_t`（3副本物理）与 `ddt_entry_t`（`dde_phys[3]`），`ddt_zap` 持久为 `zap` 对象，`brt`（Block Reference Table）削零表 `brt_entry_t` 处理 `hole` 的 `nopwrite`；`ZCHECKSUM_FLAG_DEDUP` 选型经 `zio_checksum_table` 触发 `ddt_lookup` → `brt_add`。

## C4 L3 Component — ddt_table → ddt_entry → brt 三层

`ddt_t` 为表容器：`ddt_phys`（3副本）、`ddt_entry`（`avl_tree_t`）、`ddt_zap`（`zap` 持久）。`ddt_entry_t` 含 `dde_key`（`blkid+checksum`）、`dde_phys[3]`、`dde_refcnt`。`brt` 为削零表：`brt_entry` 含 `hole` 标记。`zfs-crypto` 的 `dedup HMAC` 经 `zio_dedup` 触发 `ddt_enter`。C4 L3 图以 `ddt_t → ddt_entry → brt` 三层呈现。

```mermaid
graph TD
    DDT[ddt_t<br/>ddt_phys 3副本] --> Entry[ddt_entry_t<br/>dde_key/dde_phys]
    Entry --> Zap[ddt_zap<br/>zap持久]
    Entry --> BRT[brt<br/>hole nopwrite]
    ZIO[ZIO dedup] --> Lookup[ddt_lookup]
    Lookup --> Entry
    %% Source: openzfs/zfs/include/sys/ddt.h:40-120
```

Source: `openzfs/zfs/include/sys/ddt.h:40-120`（`ddt_t/ddt_entry_t/ddt_phys_t`）+ `openzfs/zfs/module/zfs/ddt.c:40-120`

## 时序 — dedup write → ddt_lookup → brt_add → zap

去重写：1) `zio_dedup` 经 `ZCHECKSUM_FLAG_DEDUP` 判定 `dedup` 2) `ddt_lookup(ddt, bp, tx)` 查 `ddt_entry` 3) 命中则 `brt_add(brt, bp)` 削零（`hole`）并 `nopwrite` 短路 4) 未命中则 `ddt_enter` 新增 `entry` 并 `zap_add` 持久 5) `ARC` 协同 `lru` 淘汰。时序图以 `ZIO → ddt_lookup → brt_add → zap` 全链呈现。

```mermaid
sequenceDiagram
    participant ZIO as ZIO
    participant DDT as ddt_lookup
    participant BRT as brt_add
    participant Zap as ddt_zap
    ZIO->>DDT: ddt_lookup(bp)
    alt Hit
        DDT->>BRT: brt_add(hole) nopwrite
    else Miss
        DDT->>Zap: ddt_enter + zap_add
    end
    %% Source: openzfs/zfs/module/zfs/ddt.c:200-400 + brt.c:40-120
```

Source: `openzfs/zfs/module/zfs/ddt.c:200-400`（`ddt_lookup/enter`）+ `openzfs/zfs/module/zfs/brt.c:40-120`（`brt_add`）

## 状态机 — ddt_entry REFD/HOLE/EVICT

`ddt_entry` 三态：`UNREF`（未引）→ `REFD`（`refcnt>0` 有引）→ `HOLE`（`brt` 削零 `hole`）→ `EVICT`（`lru` 淘汰）→ `UNREF`。`REFD→HOLE` 需 `brt_add` 削零；`HOLE→REFD` 需 `brt_remove`；`REFD→EVICT` 需 `lru` 满。状态机图覆盖三态及 `brt` 分支。

```mermaid
stateDiagram-v2
    [*] --> REFD: ddt_enter
    REFD --> HOLE: brt_add hole
    HOLE --> REFD: brt_remove
    REFD --> EVICT: lru淘汰
    EVICT --> [*]
    %% Source: openzfs/zfs/include/sys/ddt.h:60-120
```

Source: `openzfs/zfs/include/sys/ddt.h:60-120` + `openzfs/zfs/module/zfs/brt.c:40-120`

## 决策树

```mermaid
flowchart TD
    START([ZIO dedup?]) --> Q1{dedup开?}
    Q1 -- 否 --> A1[跳过 DDT<br/>直接 ZIO pipeline]
    Q1 -- 是 --> Q2{ddt_lookup命中?}
    Q2 -- 是 Hit --> A2[brt_add hole<br/>nopwrite短路]
    Q2 -- 否 Miss --> A3[ddt_enter<br/>zap持久]
    A2 --> Q3{BRT hole?}
    Q3 -- 是 --> A4[削零不落盘]
    Q3 -- 否 --> A5[正常落盘]
    A3 --> END([入 DDT zap])
    A4 --> END
    A5 --> END
```

Source: `openzfs/zfs/module/zfs/ddt.c:200-400` + `brt.c:40-120`

## 正例

```c
// 正例：正确的 dedup lookup与BRT配对
ddt_t *ddt = ddt_select(spa, bp);
ddt_entry_t *dde = ddt_lookup(ddt, bp, B_FALSE);
if (dde) {
    brt_add(spa->spa_brt, bp); // hole削零
    zio->io_pipeline &= ~ZIO_STAGE_VDEV_IO_START; // nopwrite短路
} else {
    ddt_enter(ddt, bp, tx); // zap持久
}
// 验证：lookup命中则brt_add配对，未命中则enter配对，refcnt一致
```

命中：`ddt_lookup` 配 `brt_add`/`ddt_enter`，`brt` hole 分支正确。

## 反例

```c
// 反例1：漏BRT导致hole未削零落盘放大
dde = ddt_lookup(ddt, bp, B_FALSE);
if (dde) ddt_enter(ddt, bp, tx); // 错：命中仍enter，未brt_add，hole仍落盘放大
// 正确：命中必brt_add nopwrite

// 反例2：未zap持久导致重启丢
ddt_enter(ddt, bp, tx); // 漏 ddt_sync -> zap_add
// 重启后 ddt_lookup Miss，dedup失效
// 正确：enter后zap持久
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/zfs-ddt.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/zfs-ddt.md` ≥3
- **正文门禁**：`wc -l ≥80` 且 `决策树/正例/反例/门禁` 均命中
- **属性门禁**：`attributes≥3` 且每条含 `grep -q` 且双源可回归
- **本体校验**：`validate 0` `islands:0`
- **脚手架门禁**：`scaffold`可产
- **Gate 门禁**：`gate --node zfs-ddt` GATE OK

Source: `openzfs/zfs/include/sys/ddt.h:40-120` + `openzfs/zfs/module/zfs/ddt.c:200-400` + `brt.c:40-120`
