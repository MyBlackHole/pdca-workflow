---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-alloc
type: entity
layer: Knowledge
status: active
summary: bcachefs Alloc 实体 — bucket 四态、open_bucket 顺序写、WFQ 分配与 background copygc/discard/reclaim 协同
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: bucket_four_state_and_open_bucket
    desc: bucket 四态 dirty/cached/need_discard/free（512K-16M）与 open_bucket 顺序写 append-only 及 bucket 字段（gen/dirty_sectors/cached_sectors/stripe）可测
    constraint: 覆盖 DOC_LATEX(allocator) bucket 四态 + bucket { gen_valid/data_type/generation/dirty_sectors/cached_sectors/stripe } + open_bucket { dev/gen/sectors_free/ec } + bucket_gens 阵列，经 C4 L3 与状态机可一图建模
    testable_signal: "运行 grep -q 'struct bucket' /home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h 且 grep -q 'open_bucket' /home/black/Documents/bcachefs-tools/fs/alloc/types.h 且 grep -q 'BUCKET' /home/black/Documents/bcachefs-tools/fs/alloc/background.c 且 grep -q 'alloc' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: wfq_foreground_and_copygc_background
    desc: foreground WFQ 选盘（1/free_space）与 background copygc 搬运、discard TRIM、journal reclaim 三协作可测
    constraint: 覆盖 foreground WFQ next_alloc+=1/free_space + alloc_request { cl/nr_replicas/watermark/target } + background move/copygc + discard_state + journal_space_from，经时序与决策树可一图建模
    testable_signal: "运行 grep -q 'bch2_alloc_sectors' /home/black/Documents/bcachefs-tools/fs/alloc/foreground.c 且 grep -q 'copygc' /home/black/Documents/bcachefs-tools/fs/alloc/background.c 且 grep -q 'journal_space_from' /home/black/Documents/bcachefs-tools/fs/journal/reclaim.c 且 grep -q 'alloc' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: buckets_gens_stale_detection
    desc: bucket_gens 代数防 stale 指针与 GC stale 检测可测
    constraint: 覆盖 bucket_gens { rcu_head/first_bucket/nbuckets/b[] } + generation 递增 + oldest_gen 窗口 + PTR_GC_BUCKET 标记 stale + backpointers 校验，经状态机与正例可一图建模
    testable_signal: "运行 grep -q 'bucket_gens' /home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h 且 grep -q 'generation' /home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h 且 grep -q 'PTR_GC' /home/black/Documents/bcachefs-tools/fs/alloc/check_data.c 且 grep -q 'alloc' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
---

# Bcachefs Alloc（空间分配）

`alloc` 为 `bcachefs` 的空间分配器：`bucket`（`fs/alloc/buckets_types.h:37`）为 512K-16M 连续区，含 `gen/dirty_sectors/cached_sectors/stripe/gen_valid`，经 `open_bucket`（`fs/alloc/types.h:44`）顺序写永不覆写，`foreground` 以 WFQ 选盘，`background` 以 `copygc` 搬运 live 数据，`discard` 发 TRIM，`reclaim` 与 `journal` 协同。定位：`src/bcachefs.rs:263` → `src/commands/device.rs` → `wrappers` → `fs/alloc/`（`foreground.c/background.c/buckets.h/discard.*`）→ `fs/bcachefs_format.h:660 alloc btree`。

## C4 L3 Component — bucket/open_bucket 与 foreground/background

`bucket`（`buckets_types.h:37` `__aligned(long)` 含 `lock/gen_valid:1/data_type:7/generation/dirty_sectors/cached_sectors/stripe_sectors`）数组按 `bucket_gens`（`rcu_head + first_bucket/nbuckets/b[]`）管理代数；`open_bucket`（`types.h:44` `spinlock/pin/freelist/hash/ec/data_type/dev/generation/sectors_free/bucket/ec*`）承接 `alloc_request`（`foreground.h:60` `cl/nr_replicas/watermark/target`）；`write_point`（`types.h:104` `hlist/mutex/last_used/data_type/ptrs`）聚合 `open_buckets`；`bch_fs_allocator`（`types.h:165` `rw_devs/freelist_lock/open_buckets[4096]/partial/write_points[32]`）为顶容器。C4 L3 图以 `allocator → write_point → open_bucket → bucket → bucket_gens` 五层呈现。

```mermaid
graph TD
    A["bch_fs_allocator<br/>alloc/types.h:165<br/>open_buckets[4096]/write_points[32]"]
    A --> WP["write_point<br/>types.h:104<br/>last_used/data_type/ptrs"]
    WP --> OB["open_bucket<br/>types.h:44<br/>dev/generation/sectors_free/ec"]
    OB --> BK["bucket<br/>buckets_types.h:37<br/>gen/dirty/cached/stripe"]
    BK --> GEN["bucket_gens<br/>types.h:47<br/>b[] 代数阵列"]
    OB --> FG["foreground WFQ<br/>foreground.c:1<br/>1/free_space"]
    FG --> BG["background copygc<br/>background.c:1"]
    BG --> DISC["discard TRIM<br/>alloc/discard.*"]
    DISC --> RC["reclaim<br/>journal/reclaim.c"]
    %% Source: /home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h:37 + fs/alloc/types.h:44 + fs/alloc/types.h:104 + fs/alloc/foreground.c:1 + fs/alloc/background.c:1
```

Source: `/home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h:37`（`bucket`）+ `/home/black/Documents/bcachefs-tools/fs/alloc/types.h:44`（`open_bucket`）+ `/home/black/Documents/bcachefs-tools/fs/alloc/types.h:104`（`write_point`）+ `/home/black/Documents/bcachefs-tools/fs/alloc/foreground.c:1` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.c:1`

## 时序 — WFQ 分配 → 顺序写 → copygc 搬运 → discard → reclaim

1) `write path` 构造 `alloc_request`（`foreground.h:60`）经 `bch2_alloc_sectors` 以 WFQ 选盘（`dev_stripe_state.next_alloc += 1/free_space` 最小者胜）；2) 取 `open_bucket` 顺序写（append-only）并递增 `bucket.generation`；3) 后台 `background.c move` 扫描 `backpointers`（`alloc/backpointers.*`）标记 stale（`PTR_GC_BUCKET`），`copygc` 搬运 live 数据至新 bucket；4) 原 bucket `dirty_sectors==0` 后进 `need_discard`，`discard.c` 发 TRIM；5) `journal reclaim` 以 `journal_space_from` 判定覆写安全后 `free`。时序图以 `request → WFQ → open_bucket → bucket → copygc → discard → reclaim` 全链呈现。

```mermaid
sequenceDiagram
    participant W as write
    participant FG as foreground WFQ
    participant OB as open_bucket
    participant BK as bucket
    participant BG as background/copygc
    participant D as discard TRIM
    W->>FG: alloc_request (replicas/watermark)
    FG->>OB: WFQ 选盘 next_alloc+=1/free
    OB->>BK: 顺序写 sectors_free-- gen++
    BG->>BK: backpointers 扫 stale
    BG->>BG: copygc 搬运 live
    BK->>D: dirty==0 → need_discard
    D->>D: discard 发 TRIM → free
    %% Source: /home/black/Documents/bcachefs-tools/fs/alloc/foreground.c:1 + fs/alloc/background.c:1 + fs/alloc/buckets_types.h:37 + fs/journal/reclaim.c:35
```

Source: `/home/black/Documents/bcachefs-tools/fs/alloc/foreground.c:1` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.c:1` + `/home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h:37` + `/home/black/Documents/bcachefs-tools/fs/journal/reclaim.c:35`

## 状态机 — bucket 四态与代数窗口

`bucket` 四态：`free → dirty → cached → need_discard → free`（`background.c:1 DOC_LATEX`）。`dirty` 含 live data，`cached` 仅 cached 副本可丢弃，`need_discard` 等 TRIM。`bucket_gens` 代数窗口 `generation - oldest_gen < BUCKET_GC_GEN_MAX=96`（`background.h:31`），`PTR_GC_BUCKET` 检测 wraparound。`open_bucket` 二态 `partial → full → closed`：`sectors_free>0` 可追加，满后入 `partial` 链表。状态机图覆盖四态与代数越界分支。

```mermaid
stateDiagram-v2
    [*] --> Free: discard 完成
    Free --> Dirty: WFQ 分配 gen++
    Dirty --> Cached: 仅 cached 副本
    Dirty --> NeedDiscard: dirty==0
    Cached --> NeedDiscard: 无 durable 副本需求
    NeedDiscard --> Free: TRIM 完成
    Free --> Dirty: 再分配
    Dirty --> Dirty: generation 递增 (防 wraparound <96)
    %% Source: /home/black/Documents/bcachefs-tools/fs/alloc/background.c:1 + fs/alloc/buckets_types.h:37 + fs/alloc/background.h:31
```

Source: `/home/black/Documents/bcachefs-tools/fs/alloc/background.c:1`（`DOC_LATEX(allocator)`）+ `/home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h:37` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.h:31`（`BUCKET_GC_GEN_MAX=96`）

## 决策树

```mermaid
flowchart TD
    START(["alloc_request"]) --> Q1{" freelist 有 free bucket? "}
    Q1 -- 是 --> WFQ["WFQ 选盘<br/>min next_alloc"]
    Q1 -- 否 --> Q2{"可 reclaim cached? "}
    Q2 -- 是 --> RC["reclaim cached → free"]
    Q2 -- 否 --> Q3{"copygc 可搬运? "}
    Q3 -- 是 --> GC["copygc live→新 bucket"]
    Q3 -- 否 --> FAIL["ENOSPC / ENOMEM restart"]
    RC --> WFQ
    GC --> WFQ
    WFQ --> Q4{" gen - oldest_gen <96? "}
    Q4 -- 否 --> FAIL
    Q4 -- 是 --> OK["open_bucket 顺序写<br/>dirty_sectors++"]
    %% Source: /home/black/Documents/bcachefs-tools/fs/alloc/foreground.c:1 + fs/alloc/background.c:1
```

Source: `/home/black/Documents/bcachefs-tools/fs/alloc/foreground.c:1` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.c:1` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.h:31`

## 正例

```c
// 正例：WFQ 分配 → 顺序写 → copygc 联动
struct alloc_request req = { .nr_replicas=2, .watermark=BCH_WATERMARK_normal, .target=... };
struct open_bucket *ob = bch2_alloc_sectors(trans, &req); // WFQ 选最小 next_alloc 的 dev
bch2_trans_update(trans, BTREE_ID_alloc, pos, &bucket_key); // 持久 alloc btree
// background: bch2_bucket_sectors_total() 判定 fragmentation，copygc 搬运 live，discard TRIM 后 free
// 验证：bucket.generation 单调，free→dirty→need_discard→free 闭环
```

命中：WFQ 与代数窗口配对，`dirty_sectors` 与 `discard` 配对。

## 反例

```c
// 反例1：绕过 trans 直接改 bucket.generation
// 错：直接写 bucket gen 丢 journal 原子性，crash 后代数不一致
// 正确：经 btree_trans 更新 BTREE_ID_alloc，再 journal 持久

// 反例2：忽略 BUCKET_GC_GEN_MAX=96 窗口
// 错：gen 差超 96 仍分配，PTR_GC_BUCKET 误判 stale 为 live
// 正确：检查 generation - oldest_gen <96 否则先 reclaim
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-alloc.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-alloc.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-alloc.md` ≥80 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-alloc --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-alloc` GATE OK

Source: `/home/black/Documents/bcachefs-tools/fs/alloc/buckets_types.h:37` + `/home/black/Documents/bcachefs-tools/fs/alloc/types.h:44` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.c:1`
