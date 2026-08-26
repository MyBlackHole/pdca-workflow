# PRD — pgwrecover 支持 PG16 多版本重放

> 状态：P3 完整规格（经 Grill 决策锁定）
> 关联：T3969（建立分发缝）、ADR-0011（pg_common 共享内核布局）、knowledge/pg/pgwrecover-multiversion-strategy.md

## 问题陈述
pgwrecover 当前仅 vendored 一份 PG18 源码整树并注册单一重放集合，无法重放 PG16 产生的 WAL。T3969 已建运行时分发缝 `pg_redo_set_for_version(control_version)`，但只注册 PG18，且缺 PG16 源码与构建期版本选择。需在源码层落地多版本（策略 B：抽取 `pg_common/` 共享内核），并接入首个新版本 PG16。

## 决策（Grill 锁定）
- 源码布局：**抽取 pg_common/ 共享内核**（ADR-0011），版本无关代码下沉，每版本只留差异 redo 与头。
- 范围：**本任务只做 PG16**；PG17 另开 PDCA 任务，沿用同一模式。
- 源码获取：**PG16 官方源码 tarball 提取**，vendored 到 `src/pg/pg16/`。
- 验收深度：每版本 **btree+GIN 端到端一致**（主 rmgr），其余 rmgr 走编译通过。

## 用户故事
- 作为数据恢复工具使用者，我希望 pgwrecover 能重放 PG16 实例的 WAL，以便在 PG16 环境做时间点恢复/增量校验。
- 作为维护者，我希望新增 PG 版本只需 vendored 差异代码并注册分发缝，不动核心分派逻辑。

## 实现决策
1. **抽取 pg_common/**：从 `src/pg/pg18/` 识别并下沉版本无关代码到 `src/pg/pg_common/`（WAL 读取框架、FPI 解压、前端内存/格式化、基础类型与页面布局头、工具头）。pg18 改为引用 pg_common/，保持 PG18 全绿。
2. **vendored PG16**：下载 PG16 源码 tarball，提取所需 xlog 前端与 redo 实现到 `src/pg/pg16/`，差异头（各 rmgr `*xlog.h`）随版本保留。
3. **构建版本选择**：`scripts/build_pgwrecover.sh` 支持目标版本（默认 PG18；`PGW_TARGET=16` 选 PG16），编译 `pg_common/` + 对应版本目录。
4. **分发缝注册**：`pg_redo_set_for_version()` 增加 `PG16_CONTROL_VERSION` 分支，返回 `pg_redo_set_pg16`（各 rmgr 指向 pg16 的 redo 实现）。新增版本仅需注册集合，核心分派零改动。
5. **fixtures 与验证**：用真实 PG16 生成 btree+GIN 的 WAL/fixtures，端到端重放后与 PG 最终态语义对比。

## 测试决策
- PG18 不变性：现有 `tests/pgwrecover/test_btree_e2e.py` 9 passed 须保持。
- PG16 新增：新建 `tests/pgwrecover/test_pg16_e2e.py`，btree+GIN 端到端一致。
- 构建：`-Wall -Wextra` 0 警告为门禁。

## 验收标准
- [ ] AC-1: 从 pg18 抽取 pg_common/ 后，PG18 构建通过且 9 passed 不变，0 警告
- [ ] AC-2: PG16 官方 tarball 提取所需文件 vendored 到 src/pg/pg16/，编译通过（0 警告）
- [ ] AC-3: 构建支持按目标版本选择（PG16/PG18），control_version=PG16 时分发缝返回 PG16 重放集合
- [ ] AC-4: PG16 fixtures（btree+GIN）端到端重放与 PG 最终态语义一致
- [ ] AC-5: 默认 PG18 回归 9 passed 不变，构建 0 警告
- [ ] AC-6: 分发缝注册 PG16，新增版本仅需注册集合（无核心分派改动）；PG17 可后续同模式接入

## Seam 分析

### 声明的测试接缝
- seam: tests/pgwrecover/test_btree_e2e.py -> src/pg/pg_replay.c
- seam: tests/pgwrecover/test_pg16_e2e.py -> src/pg/pg_replay.c

## 范围外
- 抽取 pg_common/ 后的进一步瘦身/去重优化
- PG17 及 PG<16 旧版本（PG17 另开任务）
- 流复制/分布式、性能调优

## 备注
- 复用 T3969 的 9 passed 作为 PG18 不变性基线。
- 复用 knowledge/pg/pgwrecover-official-rewrite.md（官方源码前端化方法论）与 pgwrecover-multiversion-strategy.md（策略 B）。
