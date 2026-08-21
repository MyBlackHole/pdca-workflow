# T0253 Implementation Plan

## 执行边界

本任务只在用户终审并通过 `plan -> do` 门禁后执行。T0254、T0255 与 T0257 可并行；T0258 依赖 T0255/T0257，T0259 依赖 T0258，T0256 依赖 T0254/T0259。sealed segment、immutable objects 和 manifests 是权威数据，SQLite/LMDB 仅可作为可重建派生索引。

## Batch 1

### T0254：可恢复枚举与 sealed segment

- 将递归 TREE 扫描改为持久化目录 work queue 与有界 FD 的迭代调度。
- 实现 versioned/checksummed segment、seal footer、外部排序 run、每 shard cursor 和损坏恢复。
- 对目录变化执行局部重扫，落实 `uint64_t` checked counters 与 live-tree 终止策略。

### T0255：durable segment wire 与 receipt

- 扩展 capability、幂等 batch identity、durable receipt 和客户端 cursor 提交顺序。
- 将目录元数据、硬链接及 coverage mark 纳入可恢复 record；隔离 partial 的 transfer/run/generation。

### T0257：immutable object/pack 与 segmented manifest store

- 实现 cryptographic content id、whole object、large-file chunks、small-file packs 和 sparse extents。
- 实现有界内存的 manifest segment/Merkle root、冲突检测和流式读取。

## Batch 2

### T0258：generation 发布、retention 与 GC

- 实现 object/manifest/final receipt/current-ref 的严格发布顺序和 single-writer lease。
- 实现 retained refs/pins/active leases 根集合和崩溃可恢复 GC。

## Batch 3

### T0259：backup catalog 与可恢复 restore

- 实现 generation/path metadata lookup、按原始名字节序的直属目录稳定分页和 authenticated cursor lease。
- 实现整代、目录和单路径 restore，包含目标策略、checkpoint、对象校验和 metadata dependency。

## Batch 4

### T0256：集成、迁移与性能发布门槛

- 集成 T0254/T0255，保留 T0252 为协商后的兼容回退。
- 建立 100k/1M 配对基准及崩溃矩阵，报告 CPU、RSS、I/O、sync、lookup 和重复窗口。
- 仅在故障矩阵通过且 1M 恢复 wall time 至少改善 50% 后切换默认路径。

## 关键实现顺序

1. 先固定 on-disk segment、object/manifest 与 wire receipt 的版本、校验和兼容规则。
2. 实现权威日志/immutable data 与恢复，再构建派生索引；任何索引错误不得降级为 miss。
3. 完成 publication/GC/restore 确定性崩溃测试后才做性能优化，最后执行 rollout 判定。

## 回滚

新能力使用 feature/capability gate。任一 correctness 或性能门槛失败时保持 T0252 兼容路径，不读取未受支持的新 segment；新 checkpoint 数据按 generation/TTL 清理，不影响最近成功备份。
