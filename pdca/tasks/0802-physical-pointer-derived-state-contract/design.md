# T0181 最小 physical pointer / 派生状态 / recovery 合约

## 语义来源

- `fs/data/extents.h:419-446`：extent、`btree_ptr`、`btree_ptr_v2` 都绑定
  `bch2_trigger_extent()`。
- `fs/alloc/buckets.c:620-745`：一个有效 pointer 的 transaction 路径先更新 alloc，
  再更新 backpointer；GC 是独立的 stateful 分支。
- `fs/alloc/backpointers.c:162-190`：反向桶以相应 backpointer btree 位置更新，且有独立
  校验扫描。
- `fs/init/recovery.c:288-345`：journal key replay 使用 `BTREE_TRIGGER_norun`；恢复流程
  另有显式 recovery passes（如 alloc/backpointer 检查）。
- `fs/bcachefs_format.h:1883-1890`：alloc 可从扫描重建，但该操作有明确成本；这支持把
  scan/rebuild 作为正确性合约，而非把它误称为无代价的常规路径。

## 逻辑数据边界

| 逻辑树/状态 | 身份与来源 | 权威性 | 恢复处理 |
| --- | --- | --- | --- |
| physical pointer 主键 | `extent`、`btree_ptr`、`btree_ptr_v2` 中有效 device/bucket pointer；含 owning btree id、level、key position 与 pointer identity | 唯一权威 | journal replay/根恢复后保留 |
| alloc | 每个 `(device, bucket)` 的 pointer 引用/使用状态，包含 generation 与可由 pointer 集合验证的计数 | 派生 | 从主键扫描重建 |
| backpointers | 每个有效 pointer 对应 `(bucket, owning btree id, level, key position, pointer identity)` 的反向记录 | 派生 | 从主键扫描重建 |
| accounting | 对主 pointer 集合的使用量汇总 | 派生 | 从主键扫描重算；未定义完整模型前不提供持久化 API |

`mem_ptr` 只服务当前内存 btree node 导航，不能作为物理 pointer、alloc 或 backpointer 的
来源。当前 subvol 的 `bch_fs` 无 alloc/backpointer/GC state，故该表是后续实现的格式与
恢复合约，不描述已存在的数据。

## 事务与恢复状态机

```text
physical pointer old/new
  └─ T0182: transaction trigger dispatch
       └─ T0183: old relationship remove + new relationship add
            ├─ alloc(device, bucket)
            ├─ backpointer(bucket -> owner position)
            └─ accounting

journal recovery
  ├─ replay primary pointer keys (norun is explicit)
  ├─ derived state unavailable to readers
  ├─ scan authoritative primary pointers
  ├─ rebuild alloc/backpointers/accounting deterministically
  └─ validate invariants, then publish derived state
```

Crash contract:

1. 主 pointer journal 尚未 durable：恢复不得出现该 pointer 或其派生记录。
2. 主 pointer 已 durable、派生更新尚未可见：恢复必须以主 pointer 为准完成重建，不能
   遗留旧 bucket/反向桶关系。
3. 主/派生均曾写入：恢复仍以主 pointer 扫描结果为准，避免 `norun` 导致的重复或漏记。
4. 重建/验证未完成：不得对外公开 alloc/backpointer 查询或允许基于它们进行分配。

## 可观察不变量

对每一有效 physical pointer `p`：

1. 恰有一个 alloc bucket 关系覆盖 `p.device/p.bucket`，generation 与 `p` 相容；
2. 恰有一条 backpointer 指向 `p` 的 owning `(btree, level, position)` 与 pointer identity；
3. 反向扫描得到的每条记录都能在权威主键中找到匹配 pointer；
4. replace/delete 后旧关系不存在，新关系满足 1–3；
5. journal replay + rebuild 后，派生集合等于从恢复后主键重新计算的集合。

## 范围与依赖

- T0182 实现 trigger runner/dispatch，但只在此合约已确认的 main/derived 边界内工作。
- T0183 实现派生 writer、rebuild、validator 和 crash/fault tests。
- stripe/stripe-backpointer、LRU/free-index、完整 alloc-v4 运营字段与 GC（含
  `gc_visited`）不属于本最小合约；它们需要各自完整的上游状态模型，不能以占位字段加入。
