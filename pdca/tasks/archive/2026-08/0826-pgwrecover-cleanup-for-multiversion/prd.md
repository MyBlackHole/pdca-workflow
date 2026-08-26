# pgwrecover 清理多余 PG 代码并为多版本支持建立版本边界 — 规格文档

## 问题陈述

- **现状**: src/pg/ 混入死代码（`.bak` 备份、未实现的 legacy PG9 clog 读取器），且所有重放逻辑硬编码 PG18（拷贝自 REL_18_STABLE），无版本分发边界；核心分派 `pg_replay.c` 直接绑定 PG18 实现。
- **目标**: 仅保留 PG18 支持所需代码，删除死代码，建立轻量版本分发边界，使后续 PG16/PG17 可插拔式注册。
- **差距**: 新增 PG 版本目前需侵入式改动核心分派与 redo 模块；存在确认无用的文件与函数。

## 解决方案

1. 删除确认无用的文件（`.bak` + legacy PG9 clog 读取器）。
2. 建立轻量版本边界：将版本事实集中到 `pg_versions.h`（含 PG18 条目），定义版本注册/分发点，使 `pg_replay.c` 的版本相关判断经边界而非硬编码。
3. 扫描并移除各 redo 模块中确认无调用的静态/辅助函数。
4. 确认 `stub_pg.c`/`pg_wal_stub.c` 重叠情况并合并。

## Seam 分析

### 测试接缝
- 边界层：集成测试通过 subprocess 驱动 `build/pgwrecover` 二进制，验证重放产物；本任务不新增重放逻辑，故回归即验证。
- 现有覆盖：单索引（btree/hash/gin/spgist/gist/brin/seq/freeze）+ 多索引混合 e2e 测试。
- 隔离策略：纯清理不改行为；版本边界为内部常量/分发结构，由 e2e 回归守护。

### 声明的测试接缝
- seam: tests/pgwrecover/test_btree_e2e.py -> src/pg/pg_replay.c（WAL 重放引擎及版本边界）
- seam: tests/pgwrecover/test_btree_e2e.py -> src/pg/pg_versions.h（版本事实矩阵）

### 验收可测性
- 每个 AC 均可独立 pass/fail（构建成功 + pytest PASS + 警告数）。
- 端到端：现有 e2e 全量 PASS 即证明清理未破坏行为。

## 用户故事

1. 作为维护者，我想要删除死代码，以便代码库只含 PG18 支持所需内容、降低认知负担。
2. 作为设计者，我想要版本分发边界，以便下一步添加 PG16/PG17 时只注册新版本模块、不侵改核心。

## 实现决策

- 新增/修改模块：删除 `main_pg_t0163.cpp.bak`、`pg_clog_legacy_pg9.c/.h`；扩展 `pg_versions.h` 为版本事实+分发边界（含 PG18 条目）；按需合并 stub 文件。
- 接口定义：`pg_versions.h` 暴露版本特性查询/分发点；`pg_replay.c` 经该边界做 `pg_control_version` 判断。
- 技术澄清：PG18 的 xlog 拷贝（`pg_redo_btree.c`/`pg_redo_heap_official.c` 及其 `fe_*_aux.c` 辅助）是当前必需，保留；不移动目录（目录隔离留待实际加版本时做）。
- 架构决策：版本边界仅做"集中事实 + 注册点"轻量形态，不重构 redo 实现（→ 记 `docs/adr/`）。

## 测试决策

- 被测模块：构建系统 + 重放引擎整体；行为不变，纯回归验证。
- 现有先例：单索引/多索引 e2e 已确立"重放→verify_consistency PASS"范式。

## 验收标准

- [ ] AC-1: 删除 `src/pg/main_pg_t0163.cpp.bak` 后，`bash scripts/build_pgwrecover.sh` 成功，全量 `pytest tests/pgwrecover/test_btree_e2e.py` PASS。
- [ ] AC-2: 删除 `src/pg/pg_clog_legacy_pg9.c` 与 `pg_clog_legacy_pg9.h`（未实现 legacy PG9 clog 读取器）后，构建成功且全量 pytest PASS。
- [ ] AC-3: `pg_versions.h` 集中 PG18 版本事实并定义版本分发/注册点；`pg_replay.c` 中 `pg_control_version` 相关判断经由该边界（可被注册式扩展，不硬编码 1800）。
- [ ] AC-4: 扫描各 redo 模块移除确认无调用的静态/辅助函数后，构建新增 `-Wall -Wextra` 警告数为 0，全量 pytest PASS。
- [ ] AC-5: 确认 `stub_pg.c`/`pg_wal_stub.c` 重叠；重叠则合并/删其一，构建与测试仍绿。
- [ ] AC-6: 单索引与多索引端到端测试全量 PASS（行为不变，纯清理），回归维持 9 passed。

## 范围外

- 不实现 PG16/PG17 实际重放（下一个任务）；不改动重放算法；不引入构建系统切换；不做目录级版本隔离迁移。

## 备注

- 死代码依据见 triager-brief 的 claim 验证：`.bak` 为备份；`pg_clog_legacy_pg9` 仅被注释引用、自身标注"未实现"。
- `pg_clog_reader_pg10.c`（被 `pg_heap_reader.c` 使用）保留。

---
*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
