# T0189 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0188

## 本地源码核验

- `fs/alloc/discard.c:163-219`：discard 完成后仅允许 need_discard bucket 进入 free。
- `fs/alloc/discard.c:320-375`：检查 journal boundary、open bucket、设备可写状态与 discard 能力。
- `fs/alloc/discard.c:429-539`：按 need_discard btree 遍历、提交和重试 discard work。
- `fs/alloc/background.c:1257-1455`：need_discard 派生索引与 alloc 状态变更必须同事务维护。

## 查重

T0187/T0188 已覆盖最小 reclaim API、属性模型、fault/restart；完整 discard worker 与
open-bucket 保护尚未实现，未发现同范围活动任务。

## 推荐

先完成 discard 前置条件与 open-bucket 保护，再扩展后台 worker；不引入完整 GC/LRU。
