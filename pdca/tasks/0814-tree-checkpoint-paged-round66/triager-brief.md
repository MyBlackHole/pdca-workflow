# T0252 Triage Brief

## 分类

- 类型：enhancement / architecture improvement
- 场景：development
- 父任务：T0251
- 触发：T0251 的 100k TREE checkpoint 恢复通过，但 `TreeCheckpoint::confirmed` 仍为 `unordered_map<string, uint64_t>`，状态随 namespace 线性进入进程内存。

## 查重与事实验证

- T0248/T0249 已覆盖标准 LMDB TREE checkpoint 与 no-mmap 构建门禁；T0250 仍等待实际 MDB_VL32 分支，不能替代本任务。
- T0251 已覆盖日志、事件和 100k checkpoint 语义；其结论明确不证明 checkpoint 内存边界。
- 当前代码在 `src/backupctl.cpp` 中整文件读入 `vector<uint8_t>`，再构造 `unordered_map`；100k 集成测试只证明功能，不证明 RSS 可扩展。
- SQLite 已是现有强制依赖，已有分页/预编译语句/受限 cache 的 metadata 实现可复用，但 checkpoint 的 durability 顺序必须单独验证。

## 风险

- 只把 map 换成另一种内存容器不会满足生产目标。
- 仅依赖 SQLite WAL 而不处理旧 journal 的尾部截断、重放偏移和远端 ACK 后本地落盘窗口，可能破坏断点续传安全性。
- 只跑 100k 会掩盖每路径内存增长；必须加入 1M 和 RSS 基线比较。
