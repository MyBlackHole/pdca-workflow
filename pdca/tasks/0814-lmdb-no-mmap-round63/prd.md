# T0249 Round 63：切换 LMDB no-mmap 分支并验证内存边界

## 问题陈述

T0248 的 LMDB adapter 仍链接标准 mmap LMDB。`MDB_NORDAHEAD` 不能关闭 mmap，`madvise` 只是事后回收页，无法满足部署方要求的 no-mmap 分支，也没有证明 no-mmap 分支的事务和性能边界。

## 目标

让 LMDB backend 只能在显式提供的 no-mmap 分支上启用，移除标准 LMDB 专属 mmap 假设，保持 MetadataStore、TREE checkpoint、SQLite fallback 和旧 peer 兼容，并用同条件数据重新量化 RSS/吞吐。

## 解决方案

1. Make/CMake 增加明确的 no-mmap LMDB 依赖配置和 feature probe；普通系统 LMDB 不得在 no-mmap 模式下静默通过。
2. 将 metadata_store LMDB 路径限制在 no-mmap API contract：不调用 `mdb_env_info`、映射地址、`madvise` 或 mmap-only map-size 逻辑；由 no-mmap 分支负责其内部页缓存/读写。
3. 保持完整路径键、schema 版本、事务提交/回滚、锁、generation 和 checkpoint sidecar 语义；旧 mmap cache 只能安全重建，不能静默读取为 no-mmap cache。
4. 对 no-mmap backend 运行 100k 五对 full/unchanged/changed benchmark、RSS、cache bytes、故障回滚和 checkpoint 恢复；若 no-mmap 吞吐不及 SQLite，记录明确取舍而不伪造性能达标。

## Seam 分析

- 构建接缝：`CMakeLists.txt` / `Makefile` -> `src/metadata_store.cpp`
- backend 行为接缝：`tests/metadata_backend_integration.sh` -> `src/metadata_store.cpp`
- benchmark 接缝：`tests/benchmark_metadata_index.sh` -> `src/metadata_store.cpp`
- checkpoint 回归接缝：`tests/tls_tree_checkpoint_resume_integration.sh` -> `src/backupctl.cpp` / `src/agent_tree_runtime.cpp`
- 单元接缝：`tests/unit.cpp` -> `src/metadata_store.cpp`

### 声明的测试接缝

- seam: tests/metadata_backend_integration.sh -> src/metadata_store.cpp
- seam: tests/benchmark_metadata_index.sh -> src/metadata_store.cpp
- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/backupctl.cpp
- seam: tests/unit.cpp -> src/metadata_store.cpp

## 验收标准

- [ ] AC-1: no-mmap feature probe 能识别目标分支；标准 mmap LMDB header/library 在 `LMDB_NO_MMAP=1` 下 fail-fast，不得通过 `MDB_NORDAHEAD` 冒充。
- [ ] AC-2: Make/CMake 的 no-mmap LMDB ON、LMDB OFF、TLS ON/OFF 构建无新增 warning；显式 sqlite 和 auto fallback 行为保持正确。
- [ ] AC-3: no-mmap backend 通过 full/unchanged/content-change/metadata-only/generation-mismatch/rollback/lock/corrupt-cache integration，旧 mmap cache 安全重建。
- [ ] AC-4: 100,000-entry 五对 benchmark 输出 full/unchanged/changed、entries/s、lookups、cache bytes、RSS；结果与 T0248 SQLite 基线和标准 LMDB 对照可复核。
- [ ] AC-5: no-mmap backend 不破坏 TREE checkpoint、bounded queue、目录排序、hardlink、TLS/非 TLS 和旧 peer fallback；checkpoint integration 通过。
- [ ] AC-6: 常规 unit、Make/CMake 全量回归、style check 和 TLS/非 TLS tree regression 全部通过。

## 实现决策

- no-mmap 是构建依赖属性，不由运行时 flag 猜测；只有头文件暴露 `MDB_VL32` 页管理能力时才允许 `LMDB_NO_MMAP=1`。
- 不在 no-mmap 模式保留 mmap-only 的 `madvise`/map-info 优化；内存结论以实际 RSS 和 no-mmap 分支自己的缓存语义为准。
- 标准 mmap LMDB 可作为显式实验 backend，但不得命名或报告为 no-mmap backend。

## 范围外

- 不在本轮重新设计 MetadataStore procedural C-style contract。
- 不改变 SQLite fallback、普通 single-file resume 或 TREE checkpoint wire protocol。
- 不以单次样本宣称 no-mmap 对所有存储介质都更快。
