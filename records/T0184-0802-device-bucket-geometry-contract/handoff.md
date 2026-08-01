## 当前状态

T0184 已获 confirmed verdict，Act 归档中；未修改 subvol 产品代码。

## 未完成事项

T0182 需要吸收原 T0183 范围，并实现 members-v2 live/online attach、bucket mapping、
transaction runner、pointer dispatch 与派生状态恢复。

## 已知约束

`bch_member` 已持久化 `nbuckets/first_bucket/bucket_size`；bucket 必须按上游除法/余数
映射。不可将 offset 直接当 bucket，不得在此范围加入 allocator/GC/LRU/stripe。

## 推荐的下一步

重写并终审 T0182 Plan，先建立 member attach/recovery，再实现 runner 和 alloc/backpointer
派生状态。

## 关键上下文文件列表

- `pdca/tasks/0802-transaction-trigger-runner-pointer-dispatch/prd.md`
- `records/T0184-0802-device-bucket-geometry-contract/conclusion.md`
- `knowledge/core/device-bucket-geometry-pointer-contract.md`

## Suggested skills

- `flow-plan`
- `research`
- `verify-convergence`
