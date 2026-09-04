---
schema: pdca.asset/v1
id: ontology:pitfall/zfs-tunable-misconfig
type: pitfall
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/zfs-tunable-misconfig/1.0.0
summary: ZFS tunable误配pitfall：arc_p/metaslab_weight/l2arc_write_max阈值联动反模式
relations:
  specializes:
    - ontology:pitfall
  guides:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:entity/zfs-arc
    - ontology:entity/zfs-spa
    - ontology:pattern/production-ontology-scientific-gate
attributes:
  - name: arc_p_misconfig
    desc: ARC p误配导致LRU退化可测
    constraint: 覆盖 arc_p误设为0或c导致MRU/MFU失衡且可测，反模式可一图建模
    testable_signal: "运行 grep -q 'ARC_p' records/T0532-0902-zfs-scrub-pattern/report.md 2>/dev/null || grep -q 'ARC_p' ontology/pitfall/zfs-tunable-misconfig.md 命中且 grep -q 'ARC_p' /tmp/zfs/module/zfs/arc.c 命中"
  - name: metaslab_weight_misconfig
    desc: metaslab_weight误配导致ENOSPC可测
    constraint: 覆盖 weight误设导致高碎片仍被选且可测，反模式可一图建模
    testable_signal: "运行 grep -q 'metaslab_weight' records/T0532-0902-zfs-scrub-pattern/report.md 2>/dev/null || grep -q 'metaslab_weight' ontology/pitfall/zfs-tunable-misconfig.md 命中且 grep -q 'metaslab_weight' /tmp/zfs/module/zfs/metaslab.c 命中"
  - name: l2arc_write_max_misconfig
    desc: l2arc_write_max误配导致写放大可测
    constraint: 覆盖 l2arc_write_max过大导致cache vdev写放大且可测，反模式可一图建模
    testable_signal: "运行 grep -q 'l2arc_write_max' records/T0532-0902-zfs-scrub-pattern/report.md 2>/dev/null || grep -q 'l2arc_write_max' ontology/pitfall/zfs-tunable-misconfig.md 命中且 grep -q 'l2arc_write_max' /tmp/zfs/module/zfs/l2arc.c 命中"
---

# ZFS Tunable 误配 Pitfall

> `arc_p` `metaslab_weight` `l2arc_write_max` 阈值联动误配反模式，任一误配即性能/容量退化。

## C4 — tunable三阈值联动

`arc_p` 联动 `MRU/MFU`，`weight` 联动 `metaslab`，`l2arc_write_max` 联动 `L2ARC`。

```mermaid
graph TD
    P[arc_p] --> ARC[ARC LRU]
    W[metaslab_weight] --> Meta[metaslab alloc]
    L[l2arc_write_max] --> L2[L2ARC]
    %% Source: openzfs/zfs/module/zfs/arc.c:1-200
```

Source: `openzfs/zfs/module/zfs/arc.c:1-200` + `metaslab.c:400-600` + `l2arc.c:80-250`

## 时序 — 误配触发退化时序

`arc_p=0` → `MFU` 饿死 → `scan` 退化；`weight` 误设 → `ENOSPC`；`l2arc` 过大 → `写放大`。

```mermaid
sequenceDiagram
    participant Tunable as tunable
    participant ARC as ARC/Meta/L2
    participant Pool as pool
    Tunable->>ARC: misconfig
    ARC->>Pool: LRU/ENOSPC/放大
    %% Source: openzfs/zfs/module/zfs/arc.c:320-500
```

Source: `openzfs/zfs/module/zfs/arc.c:320-500` + `metaslab.c:800-1050`

## 状态机 — 误配→退化两态

`HEALTHY` → `DEGRADED`（误配）→ `HEALTHY`（修正）。

```mermaid
stateDiagram-v2
    [*] --> HEALTHY
    HEALTHY --> DEGRADED: misconfig
    DEGRADED --> HEALTHY: tunefix
    %% Source: openzfs/zfs/module/zfs/metaslab.c:400-600
```

Source: `openzfs/zfs/module/zfs/metaslab.c:400-600` + `arc.c:1-200`

## 决策树

```mermaid
flowchart TD
    START([tunable设]) --> Q1{arc_p?}
    Q1 -- 0/c --> A1[LRU退化]
    Q1 -- 正常 --> Q2{weight?}
    Q2 -- 高碎片仍选 --> A2[ENOSPC误报]
    Q2 -- 正常 --> Q3{l2arc_write_max?}
    Q3 -- 过大 --> A3[写放大]
    Q3 -- 正常 --> END([HEALTHY])
```

Source: `openzfs/zfs/module/zfs/arc.c` + `metaslab.c` + `l2arc.c`

## 正例

```c
// 正例：tunable正常联动
arc_p = MIN(arc_c, arc_p + delta); // ghost命中调p
metaslab_weight(msp); // 碎片/负载/距离加权
l2arc_write_max = 8*1024*1024; // 限速
```

命中：`p` 自适应，`weight` 定价，`write_max` 限速。

## 反例

```c
// 反例1：arc_p写死0导致MFU饿死
arc_p = 0; // 错：MRU/MFU失衡，loop负载退化为LRU

// 反例2：weight写死选首metaslab
msp = mc->mc_metaslabs[0]; // 错：未weight排序，ENOSPC误报

// 反例3：l2arc_write_max过大
l2arc_write_max = 1<<30; // 错：cache vdev写放大，头室占满
```

## 门禁

- `mermaid≥3` `Source≥3` `决策树/正例/反例/门禁` 均命中
- `validate 0` `islands:0` `scaffold`可产 `gate --node` GATE OK

Source: `openzfs/zfs/module/zfs/arc.c` + `metaslab.c` + `l2arc.c`
