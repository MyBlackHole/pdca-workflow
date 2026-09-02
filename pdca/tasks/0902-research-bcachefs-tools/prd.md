# 调研bcachefs-tools全栈：架构、核心流与工具链

## 背景
`bcachefs-tools` 为 bcachefs 文件系统官方用户态仓库（`README.md:15` 集 `bcachefs` 主工具 + `mkfs/mount/fsck` 封装 + `fs/` 内核模块 DKMS + `man`），`GitNexus` 索引 `18058 symbols 300 flows`，含 `Rust（src/）+ C（c_src/ ccan/）` 双语言、`Cargo + Make + DKMS` 三构建。当前 PDCA 仅沉淀 ZFS 领域本体，缺对 bcachefs 的全栈心智模型与可复用本体，需一次调研达到 `production-ontology-scientific-gate` 六维可复核（`research-diagram-methodology` 6图）。

## 目标
- 以 `C4 L2/L3 + 时序 + 状态机` 多图（`mermaid≥3` 且每图1 `Source: file:line`）呈现 `bcachefs` 全栈容器（`bcachefs主工具 → 30+子命令 → wrappers/bdev/handle → fs/内核模块 → DKMS`）与 `Rust/C` 边界（`bch_bindgen/build.rs`）
- 以 `ontology/entity` 落子系统本体（**独立知识最大化**：`format/mount/fsck/device/journal/journal-rewind/btree/btree-bset/alloc/transaction/super/cli` 10+ entity/pattern/pitfall + `bcachefs-system` 聚合），每叶 `≥3 attributes` 且 `testable_signal` 双源可回归（`records + /home/black/Documents/bcachefs-tools` 源码），`scaffold` 可产，`gate --node` `GATE OK`（`ls ontology/entity/bcachefs-*.md | wc -l ≥10`）
- 以 `templates/research-report.md` 为母本产出 `records/T0533-*/research-report.md`（含 `INSTALL/Build` 工具链、`cargo metadata`/`make` 调度、`udev/initramfs` 部署），`validate 0` `islands:0` `scaffold` 可产
- 结论可被 `ontology_graph` 回链，支持后续直接派生 `to-tickets` 开发叶（叶并行根串行）
- **深化**：数据一致性（`COW + journal + btree` 原子性、`recovery_pass`）、`journal` 各记录类型（`journal_rewind_info` `list_journal` 等）的作用场景与解决的 `crash consistency` 问题、`btree` 详细实现（`kill_btree_node` `btree` 层 + `btree node/bset` 内存/磁盘格式 `bset` `bkey` 序列化）、`空间管理生命周期`（`alloc → reclaim → gc`）、`高并发支持`（`transaction restart` `lock` `BCACHEFS_INJECT_TRANSACTION_RESTARTS`）均以 `C4/时序/状态机/决策树` 可追溯

## 范围
- 输入：`/home/black/Documents/bcachefs-tools` 全树（`src/commands` 30+子命令 `c_src/` `fs/` `Makefile` `Cargo.toml` `bcachefs.8` `doc/` `scripts/install-to-kernel.sh` `fs/bcachefs/journal*` `fs/bcachefs/btree*` `fs/bcachefs/alloc*` `fs/bcachefs/super*` `src/journal_rewind_info.rs` `src/list_journal.rs` `src/btree*`），`GitNexus` 300 flows
- 输出：`records/T0533-*/research-report.md` 终版（≥6 mermaid + 每图 Source，含 `数据一致性/journal记录类型/btree/bset/空间/并发` 5章）+ `ontology/entity/bcachefs-*` **10+ entity/pattern/pitfall**（`format` `mount` `fsck` `device` `journal` `journal-rewind` `btree` `btree-bset` `alloc` `transaction` `super` `cli` 等独立知识均落本体，`ls ≥10`）+ `ontology/entity/bcachefs-system` 聚合 + `islands:0` `validate 0`
- 不做：不改 bcachefs 源码；不跑 `mkfs` 实盘压测；`verus-proofs` 仅提及来源不深

## 功能需求
1. 全栈架构：`C4 L2`（`bcachefs` → `commands` 30+ → `wrappers` → `fs/` → `DKMS`）+ `C4 L3`（`bch_bindgen` `build.rs` Rust/C 绑定）+ `部署`（`udev/initramfs/dkms`）
2. 核心执行流：`format`（`mkfs` → `super` 写入）、`mount`（`bdev→handle→ioctl→mount`）、`fsck`（`recovery_pass`）、`device`（`add/remove`）、`journal`（`journal_rewind`）、`btree`（`kill_btree_node`）至少3条时序可 `gitnexus_query` 命中
3. 本体落盘（最大化）：`bcachefs-format` `mount` `fsck` `device` `journal` `journal-rewind` `btree` `btree-bset` `alloc` `transaction` `super` `cli` 等 **10+ entity/pattern/pitfall** 各 `3 attributes`（如 `format/super/btree` `journal-rewind` `bset` `alloc` `transaction`）+ `bcachefs-system` `composed_of` 10叶，`production-ontology-gate` 六维 `GATE OK`，`ls ontology/entity/bcachefs-*.md | wc -l ≥10`
4. 工具链：`Cargo.toml` `cargo metadata` `Makefile` `VERSION:=git describe` `DKMSDIR` `make debug/install_dkms` 调度可追溯
5. 数据一致性深化：`journal + btree + COW` 原子性、`recovery_pass` 恢复、`crash consistency` 保证，以 `C4/时序/状态机` 可追溯
6. journal记录类型：`journal_rewind_info` `list_journal` `journal` 各记录类型（`JSET` `BSET` `KEY` 等）的作用场景（`crash replay` `trim` `reclaim`）与解决的问题（`原子性/回滚/空间回收`）逐类 `表格 + Source: fs/bcachefs/journal.h:line`
7. btree node/bset 格式：`btree node` 内存/磁盘格式（`bset` `bkey` `bkey_packed`）、`BSET` 磁盘序列化（`jset` 内 `bset`）、`内存 bset` 排序/压缩，以 `C4 L3 + 表格 + Source: fs/bcachefs/btree_types.h` `fs/bcachefs/bset.h` 可追溯
8. 空间管理生命周期：`alloc`（`bucket`/`freelist`）→ `reclaim`（`gc`/`discard`）→ `gc` 触发，以 `状态机 + 时序 + 决策树` 可追溯，`Source: fs/bcachefs/alloc_background.c` 等
9. 高并发支持：`transaction restart`（`BCACHEFS_INJECT_TRANSACTION_RESTARTS` `restart` 计数）、`lock`（`six` `rw`）、`多线程`（`journal` 并发、 `btree` 并发），以 `时序 + 决策树` 可追溯

## 非功能需求
- 全文中文；每图 `Source: /home/black/Documents/bcachefs-tools/... file:line` 或 `openzfs` 类比；`validate 0` `islands:0`；`testable_signal` 双源 `records + /home/...` 可 `grep -q`

## 验收标准
- [ ] AC-1 多图：`grep -c '```mermaid' records/T0533-*/research-report.md` ≥6 且 `grep -c 'Source:'` ≥6 且每图含 `file:line`（含一致性/journal/bset/空间/并发 5章各≥1图）
- [ ] AC-2 本体（最大化）：`ontology/entity/bcachefs-*.md` ≥10 且 `ls ... | wc -l ≥10` 且 `scaffold` 10叶可产且 `gate --node` 各 `GATE OK`（`format/mount/fsck/device/journal/journal-rewind/btree/btree-bset/alloc/transaction/super/cli` 等独立知识均落本体）
- [ ] AC-3 工具链：`grep -q 'Cargo.toml' records/...` 且 `grep -q 'DKMS' records/...` 且 `grep -q 'build.rs' records/...`
- [ ] AC-4 一致性/journal/btree/bset：`grep -q '数据一致性' records/...` 且 `grep -q 'journal' records/...` 且 `grep -q 'btree' records/...` 且 `grep -q 'JSET\|BSET' records/...` 且 `grep -q 'bset' records/...` 且 `grep -q 'btree_types' records/...`
- [ ] AC-5 空间/并发：`grep -q '空间管理' records/...` 且 `grep -q 'alloc' records/...` 且 `grep -q '高并发\|transaction' records/...`
- [ ] AC-6 全绿：`validate 0` + `islands:0` + `scaffold` 可产 + `validate-convergence` valid:true

## 关联本体节点
```
ontology:entity/bcachefs-system
ontology:entity/bcachefs-format
ontology:entity/bcachefs-mount
ontology:entity/bcachefs-fsck
ontology:entity/bcachefs-device
ontology:entity/bcachefs-journal
ontology:pattern/production-ontology-scientific-gate
ontology/pattern/research-diagram-methodology
```

## 拆分映射
- 全栈架构 -> research-report C4/部署
- 核心流 -> 时序/状态机
- 本体5叶 -> entity 5
- 工具链 -> report Build章
