---
schema: pdca.asset/v1
id: ontology:entity/bcachefs-system
type: entity
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/bcachefs-system/1.0.0
summary: bcachefs 全栈系统聚合（composed_of 12 叶 format/mount/fsck/device/journal/journal-rewind/btree/btree-bset/alloc/transaction/super/cli，C4 L2/L3 至 journal/btree/alloc pipeline 可建模）
relations:
  specializes:
    - ontology:concept/domain-entity
  composed_of:
    - ontology:entity/bcachefs-format
    - ontology:entity/bcachefs-mount
    - ontology:entity/bcachefs-fsck
    - ontology:entity/bcachefs-device
    - ontology:entity/bcachefs-journal
    - ontology:entity/bcachefs-journal-rewind
    - ontology:entity/bcachefs-btree
    - ontology:entity/bcachefs-btree-bset
    - ontology:entity/bcachefs-alloc
    - ontology:entity/bcachefs-transaction
    - ontology:entity/bcachefs-super
    - ontology:entity/bcachefs-cli
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:pattern/scientific-research-methodology
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:domain/bcachefs
attributes:
  - name: c4_l2_coverage
    desc: C4 L2 全栈容器覆盖
    constraint: 覆盖 bcachefs→commands(30+ leaf)→wrappers→fs/(journal/btree/alloc/sb/recovery)→DKMS 横切 Rust/C 边界，mermaid 可渲染且每图1 Source
    testable_signal: "运行 grep -q 'C4 L2' records/T0533-0902-research-bcachefs-tools/research-report.md 且 grep -q 'C4 L2' ontology/entity/bcachefs-system.md 命中且 grep -c '```mermaid' ontology/entity/bcachefs-system.md | awk '{exit !($1>=3)}'"
  - name: journal_btree_pipeline_depth
    desc: journal/btree/bset pipeline 下钻至 L3 可测
    constraint: 下钻至 jset/bset/bkey_packed 磁盘格式与 bset_tree/aux 内存格式及 journal_buf 预约环，含 bkey_format 动态位宽且 C4 L3 可建模
    testable_signal: "运行 grep -q 'jset' records/T0533-0902-research-bcachefs-tools/research-report.md 且 grep -q 'bset' records/T0533-0902-research-bcachefs-tools/research-report.md 且 grep -q 'bset' /home/black/Documents/bcachefs-tools/fs/bcachefs_format.h 命中"
  - name: twelve_leaf_completeness
    desc: 十二叶 composed_of 完整性与 100% Rule
    constraint: composed_of 恰为 12 叶 (format/mount/fsck/device/journal/journal-rewind/btree/btree-bset/alloc/transaction/super/cli) 且可 scaffold 且 ls bcachefs-*.md ≥10，符合 production-ontology-scientific-gate hundred 检查
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/bcachefs-system 检查 PASS 且 python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0' 且 ls ontology/entity/bcachefs-*.md | wc -l | awk '{exit !($1>=10)}'"
---

# Bcachefs 全栈系统（Bcachefs System）

bcachefs 全栈聚合，`composed_of` 12 叶 `format/mount/fsck/device/journal/journal-rewind/btree/btree-bset/alloc/transaction/super/cli`，以 `research-diagram-methodology` 多图 `mermaid` 为证据（C4 L2 全栈 + journal/btree pipeline 时序 + 聚合决策树），每图附 `Source: /home/black/Documents/bcachefs-tools/... file:line`。

验证：`grep -c '```mermaid' ontology/entity/bcachefs-system.md` ≥3 且 `python3 scripts/ontology-validate.py` 0 issue 且 `islands:0` 且 `production-ontology-gate --node bcachefs-system` GATE OK。

Source: `records/T0533-0902-research-bcachefs-tools/research-report.md`（8图全覆盖）+ `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263` + `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:234` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1`

## C4 L2 全栈 — bcachefs → commands → wrappers → fs/(journal/btree/alloc) → DKMS

全栈 L2：`bcachefs` 主工具（`src/bcachefs.rs:263`）→ `COMMAND_GROUPS` 8组>35 leaf（`src/commands/mod.rs:234`）→ `wrappers`（`handle/bdev/ioctl/super_io/sysfs`）→ `fs/` 五子系统 `journal(jset/bset环)`/`btree(bkey/bset/node)`/`alloc(bucket/gc)`/`sb(superblock)`/`init(recovery 26+ passes)` 横切 `Rust/C 边界(bch_bindgen/build.rs)` 与 `DKMS(fs/vendor/kernel-rust)`，C4 L2 以 `bcachefs → commands → wrappers → fs → DKMS → 块设备` 主链呈现。

```mermaid
graph TD
    User --> CLI["bcachefs<br/>src/bcachefs.rs:263"]
    CLI --> CMD["COMMAND_GROUPS 8组<br/>src/commands/mod.rs:234"]
    CMD --> W["wrappers<br/>src/wrappers/mod.rs:1"]
    W --> FS["fs/<br/>fs/bcachefs_format.h:1"]
    FS --> J["journal<br/>jset+pin+reclaim"]
    FS --> BT["btree<br/>bkey/bset/node"]
    FS --> AL["alloc<br/>bucket/gc/discard"]
    FS --> SB["sb<br/>bch_sb"]
    FS --> RC["recovery<br/>26+ passes"]
    W -. Rust/C 边界 .-> BIND["bch_bindgen/build.rs:404<br/>fs/build.rs:1"]
    FS -. DKMS .-> DKMS["DKMS<br/>Makefile:22"]
    J & BT & AL & SB & RC --> Disk["块设备"]
    %% Source: /home/black/Documents/bcachefs-tools/src/bcachefs.rs:263 + src/commands/mod.rs:234 + fs/bcachefs_format.h:1
```

Source: `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263` + `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:234` + `/home/black/Documents/bcachefs-tools/src/wrappers/mod.rs:1` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1` + `/home/black/Documents/bcachefs-tools/Makefile:22`

## 时序 — format → mount → journal → btree → alloc 全链

端到端写五步：1) `format` 经 `bch2_format` 写 `bch_sb` → 2) `mount` 经 `bdev→handle→ioctl` 触发 `bch2_fs_alloc + journal_read` → 3) `btree_trans` 预约 `journal_buf` 并 pin btree 脏页 → 4) `bset` 插入 `bkey_packed` → 5) `alloc` 经 `foreground WFQ` 分配 `open_bucket` 顺序写。时序图以 `ZPL-like → format → mount → journal → btree → alloc → Disk` 全链呈现。

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as format/mount
    participant J as journal
    participant BT as btree
    participant AL as alloc
    U->>F: format/mount/device
    F->>J: journal_res_get + pin
    J->>BT: bset 插入 bkey
    BT->>AL: bch2_alloc_sectors
    AL-->>U: 完成
    %% Source: /home/black/Documents/bcachefs-tools/fs/journal/journal.h:1 + fs/btree/types.h:645
```

Source: `/home/black/Documents/bcachefs-tools/fs/journal/journal.h:1` + `/home/black/Documents/bcachefs-tools/fs/btree/types.h:645` + `/home/black/Documents/bcachefs-tools/fs/alloc/foreground.c:1`

## 状态机 — journal/btree/alloc 联动生命周期

`journal` 三态 `empty → open → dirty → reclaim` 与 `btree` `clean → dirty → write_blocked → clean` 及 `alloc` `free → dirty → cached → need_discard → free` 联动：`journal open` 预约 `jset`，`btree dirty` pin 住 `journal seq`，`alloc dirty` 计数 `dirty_sectors`，`reclaim` 解 pin 后 `bucket` 可 discard。状态机图覆盖三子系统变迁。

```mermaid
stateDiagram-v2
    [*] --> JOpen: journal open
    JOpen --> JDirty: btree pin
    JDirty --> BDirty: btree dirty
    BDirty --> ADirty: alloc dirty
    ADirty --> Reclaim: btree 写回 + pin 释放
    Reclaim --> Free: bucket discard → free
    Free --> JOpen: 再次分配
    %% Source: /home/black/Documents/bcachefs-tools/fs/journal/journal.h:1 + fs/btree/types.h:94 + fs/alloc/background.c:1
```

Source: `/home/black/Documents/bcachefs-tools/fs/journal/journal.h:1` + `/home/black/Documents/bcachefs-tools/fs/btree/types.h:94` + `/home/black/Documents/bcachefs-tools/fs/alloc/background.c:1`

## 决策树

```mermaid
flowchart TD
    START(["用户请求 bcachefs <cmd>"]) --> Q1{"命令分组?"}
    Q1 -- format/super --> A1["super 组: bch2_format/write_super"]
    Q1 -- mount/fusemount --> A2["mount 组: bdev/handle/ioctl"]
    Q1 -- fsck/recovery --> A3["repair 组: recovery_pass 26+"]
    Q1 -- device --> A4["device 组: alloc/replicas"]
    Q1 -- debug --> A5["debug 组: dump/list_journal/kill_btree"]
    A1 & A2 & A3 & A4 & A5 --> Q2{"需事务?"}
    Q2 -- 是 --> T["btree_trans + journal pin"]
    Q2 -- 否 --> E["直接返回"]
    T --> Q3{"冲突 restart?"}
    Q3 -- 是 --> T
    Q3 -- 否 --> E
    %% Source: /home/black/Documents/bcachefs-tools/src/commands/mod.rs:234
```

Source: `/home/black/Documents/bcachefs-tools/src/commands/mod.rs:234` + `/home/black/Documents/bcachefs-tools/fs/btree/types.h:645`

## 正例

```c
// 正例：完整链路 — format → mount → write → journal → btree → alloc → reclaim 配对
// 1) format 写 super (seq 递增) 2) mount 触发 journal_read + recovery
// 3) write 经 btree_trans 预约 journal_buf 并 pin 4) alloc WFQ 选盘
// 验证：journal last_seq 单调，btree pin 与 reclaim 配对，bucket 状态闭环
```

命中：`journal last_seq` 配对，`pin/unpin` 闭环，`bucket free→dirty→free` 闭环。

## 反例

```c
// 反例1：journal pin 泄漏
// 错：btree 脏页 pin 后未在 write 回调中释放 last_seq 永不推进，journal 满死锁
// 正确：bch2_journal_pin 在 write_done 中释放，reclaim 才能回收 bucket

// 反例2：alloc 未经 trans 直接写 bucket
// 错：绕过 btree_trans 直接改 bucket.gen，丢失 journal 原子性
// 正确：经 bch2_trans_begin → alloc → trans_commit 走 journal 原子提交
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' ontology/entity/bcachefs-system.md` ≥3
- **溯源门禁**：`grep -c 'Source:' ontology/entity/bcachefs-system.md` ≥3 且每图含 `Source: /home/black/Documents/bcachefs-tools/... file:line`
- **正文门禁**：`wc -l ontology/entity/bcachefs-system.md` ≥60 且含 `决策树` `正例` `反例` `门禁`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `grep -q`
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:entity/bcachefs-system --out /tmp/x.py` 可产
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --node ontology:entity/bcachefs-system` GATE OK

Source: `records/T0533-0902-research-bcachefs-tools/research-report.md` + `/home/black/Documents/bcachefs-tools/src/bcachefs.rs:263` + `/home/black/Documents/bcachefs-tools/fs/bcachefs_format.h:1`

