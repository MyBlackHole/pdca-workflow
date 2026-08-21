# ADR-0023：无源快照的 live-tree segmented resume

## 状态

Proposed

## 背景

T0252 用 SQLite file-level confirmed map 限制内存，但恢复仍从根目录重扫，并把每文件 point lookup 与周期性同步放入海量文件关键路径。项目明确没有 source snapshot/immutable view，因此无法提供 point-in-time tree；同时不能以全量内存 map 或无限重扫换取性能。

## 决策

将大文件字节续传和目录枚举恢复分开：单文件继续使用绑定源 identity 的 partial/offset；目录任务以磁盘 work queue、append-only sealed segment 和每 shard durable cursor 为权威恢复状态。`getdents64.d_off` 不跨进程持久化，SQLite/LMDB 只能作为可重建派生索引。

远端以 `(transfer_id, shard_id, segment_id, batch_id)` 幂等提交，只有数据、依赖和 receipt 达到协商 durability 后才 ACK。live-tree 变化只局部重扫受影响目录，默认最多三轮并受 timeout 限制；超过限制返回 `INCOMPLETE/UNSTABLE`。中断运行不删除目标项，成功 final generation receipt 后才执行可恢复 mark-and-sweep。

目标端采用 versioned immutable backup repository：content-addressed objects/packs、segmented manifests 和 atomic current-ref。旧 in-place tree 仅作独立兼容模式。仓库发布必须先持久化对象和 manifest，再持久化 final receipt，最后原子切换 ref；GC 以 retained manifests 和 active-transfer leases 为根。

仓库 catalog 以 immutable generation 和 canonical path bytes 查询。目录直属 children 按原始名字节 unsigned lexicographic 排序，通过绑定 generation/root/directory/last-key 的 authenticated cursor 稳定分页。restore 支持整代、目录和单路径，逐对象校验并可断点重试；catalog/restore 均受 repository/generation/path-prefix 授权、租约和资源配额约束。

`metadata_index` 与 `resume` 是独立 job policy。metadata index 默认 off，关闭时完全不创建/打开 SQLite/LMDB/sidecar 等派生文件索引；repository manifest/catalog/restore 不受影响。resume 默认 on，关闭时不创建/读取 checkpoint、partial、receipt 或 lease，中断后新建 transfer。content-addressed object dedup 独立于 resume，不得混用语义或指标。

## 后果

- 不承诺任一时刻的全树一致快照，只承诺有界恢复、幂等传输和明确的 unstable 结果。
- 崩溃最多重做未 seal 目录或最后未持久化 batch，不以全树重扫为正常恢复路径。
- on-disk segment 和 wire receipt 需要版本、校验、迁移与 capability gate；T0252 保留为兼容回退。
- checkpoint 使用量改为磁盘有界预算，换取低 RSS 和避免每文件同步；性能是否默认启用由 1M 配对基准与故障矩阵共同决定。
- 新默认路径改变目标数据布局并要求显式 restore；换取上一成功 generation 可保留、发布可原子判定和跨任务内容复用。
