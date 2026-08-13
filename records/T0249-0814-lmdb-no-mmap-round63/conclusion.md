---
schema: pdca.asset/v1
id: T0249-0814-lmdb-no-mmap-round63
phase: check
source_ids: [do-summary, build-guard, api-scan, fallback-regression, benchmark-gap]
---

## 上下文

本轮将 LMDB 从标准 mmap 依赖切换为显式 `MDB_VL32` 页管理分支契约，并移除 adapter 中的 mmap-only 逻辑。当前环境只有 `/usr/include/lmdb.h` 与 `/usr/lib/liblmdb.so`，且该 header 不暴露 `MDB_VL32`。

## 假设与结果

| 验收标准 | 结论 |
|---|---|
| AC-1 | 通过。CMake 与 Make 均能识别并拒绝当前标准 LMDB；`MDB_VL32` 成为 no-mmap feature probe。 |
| AC-2 | 部分通过。LMDB OFF、TLS ON/OFF 构建及 CMake 配置通过；真实 VL32 ON 构建待分支依赖。 |
| AC-3 | 部分通过。SQLite integration、旧路径 fallback 与失败回滚覆盖通过；no-mmap backend 运行矩阵待依赖。 |
| AC-4 | 未完成。没有真实 no-mmap binary，不能生成 100k no-mmap 吞吐/RSS/cache bytes。 |
| AC-5 | 部分通过。TLS/非 TLS、TREE checkpoint 和 bounded queue 回归通过；no-mmap runtime 兼容性待依赖。 |
| AC-6 | 通过。Make TLS ON 全量测试、Make TLS OFF、CMake LMDB OFF、unit 与 style 通过。 |

## 分析

`MDB_NORDAHEAD` 和 `madvise` 不能替代 no-mmap 实现；本轮删除了 `mdb_env_info`、映射地址、`madvise`、`MDB_NORDAHEAD` 和 `mdb_env_set_mapsize` 路径。CMake 还会在依赖路径变化后清除并重新运行 `MDB_VL32` probe，避免缓存旧成功结果。

SQLite fallback 的功能和 checkpoint 结果没有回归。标准 mmap LMDB 的 T0248 benchmark 仅作为历史对照，未被计入本轮 no-mmap 性能结论。

## 失败原因（仅 partial）

真实 `MDB_VL32` no-mmap header/library 未安装，导致 no-mmap backend 的事务、旧 mmap cache 重建、100k benchmark、RSS 和性能取舍无法在本轮完成。这是外部依赖缺失，不是通过伪造 marker 或复用标准 LMDB 规避的实现缺陷。

## 适用边界

当前提交保证：普通系统 LMDB 不会在 no-mmap 配置下静默通过；只有显式依赖且 header 暴露 `MDB_VL32` 时才允许 LMDB 编译。它不证明任意声称支持 `MDB_VL32` 的库已经实现无 mmap 页管理，也不提供 no-mmap 性能数字。

## 下一轮建议

提供目标 `MDB_VL32` no-mmap 分支的 header/library 后，复跑 AC-2 至 AC-5：Make/CMake ON、完整 metadata integration、旧 cache 重建、故障回滚、TREE checkpoint、五对 100k benchmark、RSS 和吞吐对比。
