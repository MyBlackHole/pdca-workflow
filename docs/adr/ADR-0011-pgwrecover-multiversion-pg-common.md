# ADR-0011 — pgwrecover 多版本源码布局：抽取 pg_common/ 共享内核

- **日期**: 2026-08-26
- **状态**: 已接受
- **关联任务**: T3971-0826-pgwrecover-mv-pg16-pg17（首次落地 PG16）

## 背景

pgwrecover 当前仅 vendored 一份 PG18 源码整树（`src/pg/pg18/`），各版本重放在此单版本树上做官方源码前端化。要支持多版本（PG16/PG17/...），若继续"每版本整树拷贝"，版本无关代码（WAL 读取框架、基础类型与页面布局头、压缩/内存/格式化工具）将随版本数线性膨胀，且版本无关面一旦修改需同步 N 份。

T3969 已建立运行时分发缝 `pg_redo_set_for_version(control_version)`（按 control_version 返回 `PgRedoSet`）。但运行时分发只解决"选哪套 redo 函数"，未解决"源码如何组织多版本"。

## 决策

采用**策略 B**：将跨大版本稳定的"版本无关"代码下沉到统一共享目录 `src/pg/pg_common/`，每个 PG 大版本只保留"版本相关"的 redo 实现与少量差异头（如各 rmgr 的 `*xlog.h` 记录结构、各 `nbtxlog/heapam_xlog/ginxlog` 实现）。

- `pg_common/` 包含：WAL 读取框架、FPI 解压、前端内存/格式化工具、基础类型与页面布局头（c.h/postgres.h/varatt.h/storage/bufpage.h 等）、工具头（crc32c/port/pgtime/mb/常用 utils）。
- 每版本目录（pg16/pg18/...）包含：各 rmgr redo 实现 `.c` 与版本差异头。
- 构建按目标 `control_version` 选择编译对应版本目录 + `pg_common/`；分发缝注册对应 `PgRedoSet`。
- 首次落地：从现有 `pg18/` 抽取 `pg_common/`，保持 PG18 端到端 9 passed 不变；再加 PG16 作为首个新版本。

## 理由

- 版本无关面（heap 元组头偏移、varlena 编码、CLOG 2-bit 状态）经实测在 PG16/17/18 间一致，适合共享单一真源。
- 增量添加新版本时只引入"差异"代码，降低维护面与冲突概率。
- 与 T3969 运行时分发缝正交互补：缝管"运行期选哪套"，`pg_common/` 管"源码期组织"。
- 风险可控：先抽 `pg_common/` 并锁住 PG18 全绿，再叠加 PG16，避免一次性大改两处。

## 影响

- `src/pg/` 目录结构从"单版本整树"变为"`pg_common/` + 每版本目录"。
- 构建脚本需支持版本选择与双目录编译。
- 后续 PG17/PG18 之外版本遵循同一模式：复制差异 `.c`/头到新版本目录、注册分发缝。
- 旧"每版本整树"方案（策略 A）被否决，不再作为本仓库多版本方向。
