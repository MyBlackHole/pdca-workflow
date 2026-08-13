# T0250 Round 64 跟进：MDB_VL32 no-mmap 运行验证

## 目标

在目标 `MDB_VL32` 页管理分支 header/library 到位后，完成 T0249 延期的 LMDB runtime、兼容性和性能验收，不复用标准 mmap LMDB 数据。

## 验收标准

- [ ] AC-1: Make/CMake 的 `MDB_VL32` feature probe、TLS ON/OFF 和 LMDB ON/OFF 构建通过且无新增 warning。
- [ ] AC-2: no-mmap backend 的 full/unchanged/content-change/metadata-only/generation-mismatch/rollback/lock/corrupt-cache integration 通过，旧 mmap cache 安全重建。
- [ ] AC-3: no-mmap backend 的 TREE checkpoint、bounded queue、目录排序、hardlink、TLS/非 TLS 和旧 peer fallback 通过。
- [ ] AC-4: 五对 100,000-entry full/unchanged/changed benchmark 输出 entries/s、lookups、cache bytes、RSS，并与 SQLite 基线可复核对比。
- [ ] AC-5: 记录 no-mmap 与 SQLite 的吞吐、RSS、缓存大小取舍，不将单次结果泛化为普遍性能结论。

## 前置依赖

- 提供目标分支 `lmdb.h`，且 header 暴露 `MDB_VL32`。
- 提供与该 header 匹配的 no-mmap `liblmdb`，禁止使用 `/usr/lib/liblmdb.so` 标准实现。
- 复用 T0249 的代码提交 `12fd370`、证据和测试 seam。
