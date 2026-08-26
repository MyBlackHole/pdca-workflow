# pgwrecover 多版本 PG 支持架构策略

> 来源任务：T3969-0826-pgwrecover-cleanup-for-multiversion（用户裁定：pg18 保持 vendored 完整，源码级多版本抽取留待下一任务）。
> 关联：pgwrecover-official-rewrite.md（官方源码前端化方法论）、pgwrecover-implementation.md。

## 核心结论

多版本 PG 支持有**两层**，本任务（T3969）只建了运行时层，源码层是下一任务的范畴：

1. **运行时分发边界（已完成，T3969）**：`src/pg/pg_redo_dispatch.c` 定义 `PgRedoSet`（每 rmgr 一个 redo 函数指针）+ `pg_redo_set_for_version(control_version)`，返回对应版本集合。`pg_replay.c` 经此表分派，新增版本只需注册集合，核心分派零改动。
2. **源码级多版本（下一任务）**：PG16/PG17 的实际重放需要各自版本的 redo 实现（nbtxlog.c / heapam_xlog.c 等跨大版本结构不同），必须在源码层提供。

## 源码层两种策略（用户采纳"策略 B"方向）

- **策略 A — 每版本整树**：`pg16/` `pg17/` `pg18/` 各一份完整 vendored PG 源码拷贝。简单（PG 自身即如此），但 138 个头 × N 版本大量重复。
- **策略 B — 抽取共享内核（推荐）**：把**版本无关**的 PG 前端提到 `pg_common/`，每版本只保留**版本相关**的 redo `.c` + 少数差异头。

### 版本无关（应入 `pg_common/`，跨大版本基本稳定）
- WAL 读取框架：`xlogreader.c`、`pg_lzcompress.c`（FPI 解压）、`fe_memutils.c`、`snprintf.c`
- 基础类型/布局：`c.h`、`postgres.h`、`postgres_fe.h`、`varatt.h`、`storage/bufpage.h`、`storage/item*.h`、`storage/off.h`、`storage/block.h`、`storage/relfilelocator.h`
- 工具：`port/pg_crc32c.h`、`port.h`、`pgtime.h`、`mb/pg_wchar.h`、`utils/*.h`（datum/elog/hashfn）
- 依据 `pg_versions.h` 实测：heap 元组头偏移、varlena 编码、CLOG 2-bit 状态各版本一致。

### 版本相关（应留每版本目录）
- 各 rmgr redo 实现：`pg_redo_btree.c`(=nbtxlog.c)、`pg_redo_heap_official.c`(=heapam_xlog.c)、`fe_gin_aux.c`(=ginxlog.c)、`fe_gist_aux.c`、`fe_spgist_aux.c`、`fe_brin_aux.c`、`fe_hash_aux.c`、`pg_redo_seq_official.c`
- 版本差异头：`access/heapam_xlog.h`、`access/nbtxlog.h`、`access/ginxlog.h`、`access/gistxlog.h` 等（rmgr 记录结构随版本演变）
- CLOG 目录名迁移事实：`pg_versions.h` 已记 PG10+ 为 `pg_xact/`、PG9.x 为 `pg_clog/`

## 实施顺序（下一任务参考）

1. 从 `pg18/` 抽取上述"版本无关"部分到 `pg_common/`，验证 PG18 构建仍绿、9 passed 不变。
2. 克隆 `pg18/` 为 `pg16/`、`pg17/`（用对应 PG 大版本源码替换 redo `.c` 与差异头）。
3. 在 `pg_redo_dispatch.c` 增 `pg_redo_set_pg16` / `pg_redo_set_pg17` 并注册到 `pg_redo_set_for_version()` 的 `switch`。
4. 构建脚本按 `control_version` 选择编译对应版本源；CI 用 PG16/PG17 容器生成 fixtures 做端到端回归。

## 风险/注意

- 抽取 `pg_common/` 改动 vendored 树，须以"构建 0 警告 + 9 passed 不变"为门禁（见 T3969 AC-4/AC-6）。
- `pg18/` 当前保持完整，是因为它是 PG18 参考单元，也是抽取 `pg_common/` 的来源；不要为瘦身而删单个头（有编译风险）。
- 死代码清理（T3969）已移除：`.bak`、`pg_clog_legacy_pg9.c/.h`、`stub_pg.c`、pgbin 全套、`fix_infomask_from_infobits` 死函数。
