# T0252 PRD：磁盘分页 TREE checkpoint 与海量断点续传

## 问题

当前 TREE checkpoint 在恢复时把整个 checkpoint 文件读入 `vector<uint8_t>`，随后将所有路径和 fingerprint 放入 `std::unordered_map`；运行中还累积未提交的 `pending` 路径。海量文件、断电恢复和多次重试时，进程 RSS 随 namespace 线性增长，无法满足生产级海量备份。

## 目标

将 confirmed 状态改为磁盘有序索引，逐条/分页查询当前路径，pending 受固定上限约束；保留现有 checkpoint 协议、远端 ACK 后本地持久化、generation/options 隔离、fingerprint 变更检测、损坏尾部截断和安全重放语义。实现必须在 100k 与 1M 规模给出 RSS、恢复吞吐、跳过率和重发量证据。

## 非目标

- 不在本轮切换 LMDB 到不存在的系统 `MDB_VL32` 分支；T0250 独立负责供应链和真实 no-mmap 运行验证。
- 不改变远端 TREE_CHECKPOINT/ACK 帧格式和备份目标目录语义。
- 不以关闭 checkpoint、全量重传或把整个文件映射进用户态作为“内存优化”。

## 方案概要

抽取 `TreeCheckpoint` 到独立模块，使用现有 SQLite 依赖维护 checkpoint sidecar B-tree：`entries(path PRIMARY KEY, fingerprint)` 与 `meta(generation, options, journal_offset, next_batch)`。原有 `.tree-checkpoint` 保留为可流式扫描的 append journal，兼容旧文件并作为崩溃重放源；恢复只使用预编译的 point lookup 和固定大小批量事务，不构造全量路径 map。journal 已 fsync 但 index 尚未提交时，启动阶段从 `journal_offset` 重放；非法/截断尾部从 record 起点截断。generation/options 不匹配时原子重建 index。

写入顺序维持现有安全边界：先发送 batch、验证 `TREE_CHECKPOINT_ACK`，再 append journal + fsync，随后在有界 SQLite transaction 中 upsert，并提交 journal offset。checkpoint 临时 pending 以固定 entry/bytes 双上限控制，达到上限即通过当前 session flush；任何本地持久化失败都停止操作而不清空未确认状态。SQLite page cache 设为固定负值并记录 cache hit/miss，不能以默认无界缓存冒充 O(1) RSS。

## 用户故事

- 作为海量文件备份操作者，我希望断电后恢复不因读取全部 checkpoint 路径而耗尽内存。
- 作为运维人员，我希望源文件改变、checkpoint 尾部损坏或 generation 改变时只重发不安全项，而不是静默跳过。
- 作为性能工程师，我希望能分别看到 RSS、恢复吞吐、跳过率和重复发送量，避免单一“测试通过”掩盖退化。

## 验收标准

- [ ] AC-1: `TreeCheckpoint` 使用独立模块和磁盘 B-tree/分页查询；代码路径不再创建全量 `confirmed` map 或按文件大小分配完整 journal buffer，pending 同时受 entry 与 bytes 上限约束。
- [ ] AC-2: 新建、重启、generation/options 变化、非法尾部截断、远端 ACK 后进程崩溃重放、旧 v1 journal 迁移、sidecar 单进程锁和原子迁移均有测试；源文件 fingerprint 改变只导致对应条目重发，SQLite lookup 错误不得被当作 miss。
- [ ] AC-3: 100k 与 1M checkpoint 基准记录 wall time、CPU、peak RSS、checkpoint bytes、SQLite page-cache 配置；1M 恢复的峰值 RSS 不得随路径表按线性比例增长，并满足报告中预先声明的固定上限。
- [ ] AC-4: 100k/1M 断点恢复记录 skipped、resent、duplicate-safe 结果和恢复吞吐；未改变条目不重复发送，损坏尾部不会静默确认缺失条目。
- [ ] AC-5: Make、CMake TLS ON/OFF、unit、TREE checkpoint、增量、完整回归和 style 检查全部通过；旧文本进度输出和 T0251 日志事件兼容。
- [ ] AC-6: 设计文档、迁移/回滚说明、性能报告和 evidence manifest 可复核，明确 SQLite sidecar、journal offset、durability 窗口、无 mmap/固定 page cache、文件锁和失败处置。

## 测试策略

- 单元：journal 流式解析、坏尾截断、generation/options 隔离、point lookup、批量事务、pending 上限和重放偏移。
- 集成：断电/kill 注入、源文件变更、100k 与 1M TREE 恢复，验证目标文件数量、内容、skip/send 计数和副作用。
- 性能：每个规模至少三次取中位数；分别对比 baseline 与 disk-index 的 wall/CPU/RSS，不把日志开关或单次偶然快慢当作结论。

## Seam 分析

### 声明的测试接缝

- seam: tests/tls_tree_checkpoint_resume_integration.sh -> src/tree_checkpoint.cpp
- seam: tests/tree_checkpoint_paged_benchmark.sh -> src/tree_checkpoint.cpp
- seam: tests/unit.cpp -> src/tree_checkpoint.cpp

## 范围外与回滚

若 sidecar 初始化、迁移或 replay 失败，必须 fail closed 并保留原 journal；不得删除可恢复数据。发布回滚通过 feature gate 回到 legacy journal 只读/全量重发路径，但性能验收不得以回滚路径冒充完成。迁移完成前保留原文件和明确版本标记。
