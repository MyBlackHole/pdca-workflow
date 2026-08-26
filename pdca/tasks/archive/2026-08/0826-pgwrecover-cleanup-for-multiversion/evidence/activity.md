# Do 阶段活动记录 — T3969 清理多余 PG 代码并为多版本支持建立版本边界

## 执行摘要
清理 pgwrecover 中多余/未使用的 PG 代码，建立轻量版本分发边界，使后续可插拔 PG16/PG17。

## 关键步骤
1. **删死代码（AC-1/AC-2/AC-5）**
   - `src/pg/main_pg_t0163.cpp.bak`：未跟踪的备份垃圾，直接 `rm`。
   - `src/pg/pg_clog_legacy_pg9.c/.h`：仅注释引用、自身标注"未实现"的 legacy PG9 clog 读取器，`git rm`。
   - `src/pg/stub_pg.c`：构建脚本 `build_pgwrecover.sh` 从未编译的死桩（活跃桩是 `pg_wal_stub.c`），`git rm`。
   - pgbin 全套（用户裁定移除）：`pgbin.cpp`、`pg_heap_reader.c/.h`、`pg_clog_reader_pg10.c/.h`、`build_pgbin.sh`——依赖已移除的 `third_party/pg184`，本就失效。
2. **版本边界（AC-3）**
   - `src/pg/pg_versions.h`：增 `PG18_CONTROL_VERSION 1800`，清理已删文件注释，加分发缝说明。
   - 新增 `src/pg/pg_redo_dispatch.h/.c`：`PgRedoSet`（每 rmgr 一个 redo 函数指针）+ `pg_redo_set_for_version(control_version)`，注册 PG18 集合。
   - `src/pg/pg_replay.c`：入口选取 `set = pg_redo_set_for_version(PG_BASE_VER)`，分派经 `set->xxx`，删除原重复的 `RM_GIST_ID` 死分派块（line 331，注释误标"Sequence rmgr"）。
3. **未用函数（AC-4）**
   - 删死函数 `fix_infomask_from_infobits`（fe_heap_aux.c 中的死副本，真身在 pg_redo_heap_official.c）。
   - 构建加 `-Wall -Wextra`：vendored PG 拷贝以 `-Wno-unused-variable` 放宽；自有逻辑模块严格。0 警告 0 错误。
4. **bug 修复**
   - 分派重构时一度误将 GIN 指到 `set->gist`（应为 `set->gin`），已修正并回归验证。
   - `pg_wal_stub.c` 的 `pg_strerror` 加 `#undef strerror` 消除 `-Winfinite-recursion` 误报。
   - `pgwrecover.cpp` 日志/JSON `snprintf` 截断为良性，加文件级 `-Wformat-truncation` pragma。
5. **回归（AC-6）**：全量 `pytest tests/pgwrecover/test_btree_e2e.py` 9 passed（含 GIN/多索引），构建 0 警告。

## 用户裁定（Check 阶段）
- `src/pg/pg18/` 是 vendored PG18 参考实现，保持完整（多版本时作 pg18 同级单元）；源码级多版本抽取（策略 B：抽取版本无关内核到 pg_common/）留待下一任务。
- 多版本架构策略沉淀：`knowledge/pg/pgwrecover-multiversion-strategy.md`。

## 产物 digest（sha256）
- src/pg/pg_redo_dispatch.c: 7592b7a1ee50cc456f9ce29800e590a9dd7e74d3577eeb4d3859d0addc4dc278
- src/pg/pg_redo_dispatch.h: 3f1c9d3613df199dd4c6ffa4b3fda120ebb5a887dc38286c01d5f796a9e7d22c
- src/pg/pg_replay.c: a48116149d339e29f5bf1443ddf4c9f91e78bcfca943c689ecd5baf2f45e69be
- src/pg/pg_versions.h: 871a51e6325b1da93fbe0c9859051166960e466e2272d74f6936098f84527d63
- scripts/build_pgwrecover.sh: 0c404e2feaca30aabe12107d58b4fe03cf1294e0094ee59d711d4f1aa93e7495
- src/pg/fe_heap_aux.c: 5765d77512994853f8af0474dedd3995e7e6f3cd15c6dc3ec72bdd6035e5ba14
- src/pg/pg_wal_stub.c: 58a3dff33ed42aa936ee6c7df9f036196587b6d94d5d95ba3ab5150742a75954
- src/pg/pgwrecover.cpp: 804f7ce4eea4a39208e722c527500a3d6efbdabbd32cd670414b6ab400925946
