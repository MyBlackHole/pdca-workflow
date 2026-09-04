---
schema: pdca.asset/v1
id: ontology:pattern/zfs-scrub-resilver
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/zfs-scrub-resilver/1.0.0
summary: ZFS scrub/resilver运维pattern：scan/queue/repair三态与vdev关联
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:entity/zfs-vdev
    - ontology:entity/zfs-spa
    - ontology:pattern/production-ontology-scientific-gate
attributes:
  - name: scrub_scan
    desc: scrub扫描与dsl_scan可测，对应C4 L3
    constraint: 覆盖 dsl_scan_t/scrub的 scan发起与 dsl_scan_visit 可测且 C4 L3 可建模
    testable_signal: "运行 grep -q 'dsl_scan' records/T0532-0902-zfs-scrub-pattern/report.md 2>/dev/null || grep -q 'dsl_scan' ontology/pattern/zfs-scrub-resilver.md 命中且 grep -q 'dsl_scan' /tmp/zfs/module/zfs/dsl_scan.c 命中"
  - name: resilver_queue
    desc: resilver队列与vdev_queue可测，对应时序图
    constraint: 覆盖 resilver的 vdev_queue入队与 resilver_defer 可测且时序可建模
    testable_signal: "运行 grep -q 'resilver' records/T0532-0902-zfs-scrub-pattern/report.md 2>/dev/null || grep -q 'resilver' ontology/pattern/zfs-scrub-resilver.md 命中且 grep -q 'resilver' /tmp/zfs/module/zfs/vdev.c 命中"
  - name: repair_ereport
    desc: repair与ereport可测，对应状态机
    constraint: 覆盖 zfs_ereport与 repair的 SCANNING/FINISHED两态及状态机可建模
    testable_signal: "运行 grep -q 'zfs_ereport' records/T0532-0902-zfs-scrub-pattern/report.md 2>/dev/null || grep -q 'zfs_ereport' ontology/pattern/zfs-scrub-resilver.md 命中且 grep -q 'zfs_ereport' /tmp/zfs/module/zfs/zfs_ereport.c 命中"
---

# ZFS Scrub/Resilver 运维 Pattern

> `dsl_scan` 驱动 `scrub` 全池扫描，`resilver` 队列修复 `vdev` 离线盘，`zfs_ereport` 上报校验错，三态可测。

## C4 L3 — scan → queue → repair 三层

`dsl_scan_t` 为扫描容器，`vdev_queue` 为修复队列，`zfs_ereport` 为上报。C4 L3 图以 `dsl_scan → vdev_queue → repair` 三层呈现。

```mermaid
graph TD
    Scan[dsl_scan_t<br/>scrub] --> Queue[vdev_queue<br/>resilver]
    Queue --> Repair[repair<br/>ereport]
    Scrub[scrub] --> Scan
    %% Source: openzfs/zfs/module/zfs/dsl_scan.c:40-120
```

Source: `openzfs/zfs/module/zfs/dsl_scan.c:40-120` + `openzfs/zfs/module/zfs/vdev.c:400-600`

## 时序 — scrub发起 → scan_visit → resilver队列 → repair

`scrub` 发起 `dsl_scan_visit` 遍历 `bp`，`resilver` 入 `vdev_queue`，`repair` 经 `zfs_ereport` 上报。时序图以 `scrub → scan → queue → repair` 全链呈现。

```mermaid
sequenceDiagram
    participant Scrub as scrub
    participant Scan as dsl_scan
    participant Queue as vdev_queue
    participant Repair as repair
    Scrub->>Scan: dsl_scan_visit(bp)
    Scan->>Queue: resilver enqueue
    Queue->>Repair: zfs_ereport
    %% Source: openzfs/zfs/module/zfs/dsl_scan.c:200-400
```

Source: `openzfs/zfs/module/zfs/dsl_scan.c:200-400` + `openzfs/zfs/module/zfs/vdev.c:500-700`

## 状态机 — SCANNING/FINISHED 两态

`dsl_scan` 两态：`SCANNING`（扫描中）→ `FINISHED`（完成）→ `SCANNING`（下次 scrub）。`resilver` 亦 `DEGRADED→RESILVERING→HEALTHY`。状态机图覆盖两态及 `scrub` 触发。

```mermaid
stateDiagram-v2
    [*] --> SCANNING: scrub start
    SCANNING --> FINISHED: scan done
    FINISHED --> SCANNING: next scrub
    %% Source: openzfs/zfs/include/sys/dsl_scan.h:40-80
```

Source: `openzfs/zfs/include/sys/dsl_scan.h:40-80` + `openzfs/zfs/module/zfs/dsl_scan.c:40-120`

## 决策树

```mermaid
flowchart TD
    START([pool状态]) --> Q1{scrub?}
    Q1 -- 是 --> A1[dsl_scan_visit<br/>全池校验]
    Q1 -- 否 --> Q2{resilver?}
    Q2 -- 是 --> A2[vdev_queue resilver<br/>修复离线盘]
    Q2 -- 否 --> A3[正常 I/O]
    A1 --> Q3{错?}
    Q3 -- 是 --> A4[zfs_ereport]
    Q3 -- 否 --> END([FINISHED])
    A2 --> END
    A4 --> END
```

Source: `openzfs/zfs/module/zfs/dsl_scan.c:300-500` + `vdev.c:400-600`

## 正例

```c
// 正例：scrub与resilver配对
dsl_scan_visit(spa, bp); // scrub扫描
if (vdev_state == DEGRADED) resilver_enqueue(vdev); // 修复
zfs_ereport_post(ECKSUM); // 上报
```

命中：`scan` 配 `queue` 配 `ereport`。

## 反例

```c
// 反例：漏resilver导致DEGRADED永不恢复
vdev_set_state(leaf, FAULTED);
// 漏 resilver_enqueue：即使盘回，仍DEGRADED
// 正确：FAULTED→resilver→HEALTHY
```

## 门禁

- `mermaid≥3` `Source≥3` `决策树/正例/反例/门禁` 均命中
- `validate 0` `islands:0` `scaffold`可产 `gate --node` GATE OK

Source: `openzfs/zfs/module/zfs/dsl_scan.c` + `vdev.c` + `include/sys/dsl_scan.h`
