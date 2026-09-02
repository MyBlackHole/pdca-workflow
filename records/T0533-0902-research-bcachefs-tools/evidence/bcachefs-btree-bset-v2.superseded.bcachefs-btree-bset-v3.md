---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-btree-bset
type: entity
layer: Knowledge
status: active
summary: bcachefs Bset 实体 — bset 磁盘格式（seq/journal_seq/u64s + bkey_packed 变长）与内存 bset_tree 辅助树（BSET_CACHELINE=256 浮点路标）及 bkey 序列化
relations:
  specializes:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: bset_disk_mem_dual_format
    desc: bset 磁盘/内存双格式（磁盘 bset + bkey_packed 变长整数 vs 内存 bset_tree + aux 二叉堆）及 bkey_format 动态位宽可测
    constraint: 覆盖 struct bset { seq/journal_seq/flags/version/u64s + bkey_packed _data[0] } + struct bset_tree { size/extra/data_offset/aux_data_offset/end_offset } + BSET_CACHELINE=256 每 256B 一 float 路标 + bkey_format 6 字段（inode/offset/snapshot/size/version）动态位宽，经 C4 L3 与时序可一图建模
    testable_signal: "运行 grep -q 'struct bset' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h && grep -q 'bset_tree' /home/black/Documents/bcachefs-tools/fs/btree/types.h && grep -q 'BSET_CACHELINE' /home/black/Documents/bcachefs-tools/fs/btree/bset.h 且 grep -q 'btree-bset' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: bkey_pack_unpack_and_wrapper
    desc: bkey 压缩/解压（high_word 变长 + unpack[6] 解码）与 bkey_s_c/bkey_i_* 包装可测
    constraint: 覆盖 bkey_types.h:21 的 bpos/bkey (u64s/format/type/pad + bversion + size + p) + bkey_packed (_data[0] 7b format) + high_word 双实现 + bkey_s_c {k,v} + x-macro 展开 bkey_i_extent 等，经 C4 L3 与正例可一图建模
    testable_signal: "运行 grep -q 'bkey_packed' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h && grep -q 'bkey_s_c' /home/black/Documents/bcachefs-tools/fs/btree/bkey_types.h && grep -q 'bkey_i_' /home/black/Documents/bcachefs-tools/fs/btree/bkey_types.h 且 grep -q 'btree-bset' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
  - name: bset_lifecycle_and_gc_sorted
    desc: bset 生命周期（RW_AUX 可写 → RO_AUX 只读 → sorted/lazy → compact）与 GC stale 过滤可测
    constraint: 覆盖 MAX_BSETS=3 + want_new_bset 取 last + bch2_bset_init_next + bset_build_aux_tree (RW→RO) + sort 懒排序 + compact 合并 + ptr_invalid 过滤 size0 与 stale（gc 保留 until rewrite），经状态机与决策树可一图建模
    testable_signal: "运行 grep -q 'MAX_BSETS' /home/black/Documents/bcachefs-tools/fs/btree/bset.h && grep -q 'bch2_bset_init_next' /home/black/Documents/bcachefs-tools/fs/btree/bset.h && grep -q 'want_new_bset' /home/black/Documents/bcachefs-tools/fs/btree/bset.h 且 grep -q 'btree-bset' records/T0533-0902-research-bcachefs-tools/research-report.md 命中"
---

# Bcachefs Btree Bset（B 树 Bset/键格式）

`bset` 为 `btree_node` 内 `bkey` 容器：磁盘 `bset`（`bcachefs_format.h:1902`）为 `bkey_packed` 变长数组，内存 `bset_tree`（`btree/types.h:49`）以 `BSET_CACHELINE=256` 浮点路标建二叉堆 `aux`，`bkey_format` 动态压缩 `bpos` 三字段。`bkey`（`bkey_types.h:21`）以 `bkey_s_c/bkey_i` 包装访问。定位：`fs/btree/bset.h:150`（`BSET_CACHELINE`）→ `bset.c` → `fs/bcachefs_format.h:1902/260` → `fs/btree/types.h:49/94`。

## C4 L3 Component — 磁盘 bset/bkey_packed vs 内存 bset_tree/aux

磁盘：`bset { seq/journal_seq/flags/version/u64s + bkey_packed _data[0] }`（`1902`）内 `bkey_packed { _data[0] + u64s + 7b format/type/pad }`（`260`）视多词整数存 `bpos`；内存：`bset_tree { size/extra/data_offset/aux_data_offset/end_offset }`（`49`）按 `BSET_CACHELINE=256`（`bset.h:150`）每 256B 取一 `bkey_float` 为路标，`aux_data` 存二叉堆数组（`to_inorder` 索引），`btree { set[3] + bkey_format + unpack[6] }`（`94`）聚合。`bkey_format` 6 字段位宽表经 `unpack[6] { byte_offset/shift }` 解码。C4 L3 图以 `bset(磁盘) → bkey_packed(变长) → bset_tree(内存路标) → btree.set[3]` 四层呈现。

```mermaid
graph TD
    BSET["bset:1902<br/>seq/journal_seq/u64s<br/>+ _data[0]"]
    BSET --> BP["bkey_packed:260<br/>_data[0] 变长<br/>u64s+format/type"]
    BP --> BT["bset_tree:49<br/>size/data_offset<br/>aux_offset/end"]
    BT --> AUX["aux 二叉堆<br/>bset.h:150<br/>BSET_CACHELINE=256<br/>bkey_float 路标"]
    AUX --> FMT["bkey_format<br/>6字段位宽<br/>unpack[6]"]
    FMT --> BTR["btree.set[3]<br/>types.h:94<br/>MAX_BSETS=3"]
    %% Source: /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1902 + fs/bcachefs_format.h:260 + fs/btree/types.h:49 + fs/btree/types.h:94 + fs/btree/bset.h:150
```

Source: `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1902`（`bset`）+ `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:260`（`bkey_packed`）+ `/home/black/Documents/bcachefs-tools/fs/btree/types.h:49`（`bset_tree`）+ `/home/black/Documents/bcachefs-tools/fs/btree/types.h:94`（`btree.set[3]`）+ `/home/black/Documents/bcachefs-tools/fs/btree/bset.h:150`（`BSET_CACHELINE=256`）

## 时序 — bset 插入 → aux 构建 → 读时二分

1) `want_new_bset()取 bset_tree_last`；2) `bch2_bset_init_next` 分配新 `bset`（`RW_AUX` 可写）；3) 新 key 仅插 `未写 bset`（`bkey_to_bset`）；4) 满时 `bch2_bset_build_aux_tree` 转 `RO_AUX`（二叉堆固化）；5) 读时 `bset()` 经 `data_offset/end_offset` 定位 `vstruct_last`，`aux` 二分到 256B 路标后线性探查；6) `>MAX_BSETS` 时 `compact` 合并压缩，`ptr_invalid` 过滤 size0。时序图以 `init_next → insert(RW) → build_aux(RO) → search(aux) → compact` 全链呈现。

```mermaid
sequenceDiagram
    participant W as write
    participant BS as bset RW
    participant AUX as aux 二叉堆
    participant R as read
    W->>BS: want_new_bset() → last
    W->>BS: bch2_bset_init_next (RW_AUX)
    W->>BS: bch2_bset_insert RW
    BS->>AUX: bch2_bset_build_aux_tree → RO
    R->>AUX: bset() + aux 二分 (256B路标)
    AUX-->>R: бkey_packed → unpack→bkey_s_c
    Note over R: >3 bsets → compact合并
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/bset.h:279 + fs/btree/types.h:49 + fs/btree/bset.c:1
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/bset.h:279`（`keys_init/init_first/next/build_aux_tree/insert`）+ `/home/black/Documents/bcachefs-tools/fs/btree/types.h:49` + `/home/black/Documents/bcachefs-tools/fs/btree/bset.c:1`

## 状态机 — bset RW→RO→sorted→compact 循环

`bset_tree` 四态 `RW_AUX → RO_AUX → sorted → compact`：`RW` 唯一可写，写满或刷盘即 `RO`（只读+二叉堆固化），`>4 bsets` 懒 `sorted`，`MAX_BSETS=3` 时 `compact` 合并。`bkey` 二态 `packed ↔ unpacked`：写时 `pack`（高位截断），读时 `unpack`（`unpack[6]`）。`aux` 二态 `NO_AUX → RO/RW_AUX`：`RO_AUX` 预建，`RW_AUX` 增量维护。状态机图覆盖 `RW→RO→compact→RW` 往返。

```mermaid
stateDiagram-v2
    [*] --> RW: bch2_bset_init_next
    RW --> RO: build_aux_tree
    RO --> Sorted: 懒排序 (>4 bsets)
    Sorted --> Compact: compact 合并
    Compact --> RW: 新 bset 承接
    RO --> GC: gc 时 ptr_invalid 过滤 stale
    GC --> RW: copygc 后旧 bset 释放
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/bset.h:279 + fs/btree/types.h:49 + fs/btree/bset.c:1
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/bset.h:279` + `/home/black/Documents/bcachefs-tools/fs/btree/types.h:49` + `/home/black/Documents/bcachefs-tools/fs/btree/bset.c:1`

## 决策树

```mermaid
flowchart TD
    START(["需插入 bkey"]) --> Q1{"有可写 RW bset?<br/>want_new_bset"}
    Q1 -- 否 满3 --> C["compact 合并 oldest"]
    C --> Q1
    Q1 -- 是 --> W["bch2_bset_insert RW"]
    W --> Q2{"读时定位?"}
    Q2 -- aux 命中 --> AUX["aux 二分→256B路标→线性探查"]
    Q2 -- bkey 边界 --> P["bkey_packed unpack<br/>high_word 判"]
    AUX & P --> Q3{"stale/size0?"}
    Q3 -- 是 size0 --> F1["ptr_invalid 过滤"]
    Q3 -- 是 stale --> F2["gc 保留 until rewrite"]
    Q3 -- 否 live --> OK(["返回 bkey_s_c"])
    %% Source: /home/black/Documents/bcachefs-tools/fs/btree/bset.h:348 + fs/btree/types.h:49
```

Source: `/home/black/Documents/bcachefs-tools/fs/btree/bset.h:348`（`want_new_bset`）+ `/home/black/Documents/bcachefs-tools/fs/btree/types.h:49`

## 正例

```c
// 正例：bkey 变长压缩 → bset 追加 → aux 加速
struct bkey_i *k = bkey_next(prev); k->k.u64s = ...; k->k.type = KEY_TYPE_extent;
bch2_bkey_to_bset(btree, k); // 仅插 RW bset
bch2_bset_build_aux_tree(btree, t); // RO 后建二叉堆
struct bkey_s_c found = bch2_bset_search(btree, pos); // aux 二分 + unpack
// 验证：u64s 含 header，type 断言 bkey_s_c_to_extent 前检查
```

命中：`RW` 唯一可写与 `RO` 只读配对，`pack/unpack` 可逆。

## 反例

```c
// 反例1：向 RO bset 插入
// 错：bch2_bset_insert 到已 RO_AUX 的 bset，aux 索引错乱
// 正确：仅 RW_AUX 的 last bset 可 insert（want_new_bset 保障）

// 反例2：裸读 bkey 不经 unpack
// 错：直接取 bkey_packed 的 _data 字段，位宽错误
// 正确：经 unpack[6] 解码后得 bpos 再 bkey_s_c 包装
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-btree-bset.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-btree-bset.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-btree-bset.md` ≥80 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q` 且双源可回归
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-btree-bset --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-btree-bset` GATE OK

Source: `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1902` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:260` + `/home/black/Documents/bcachefs-tools/fs/btree/types.h:49`
