# T0182 合并实现设计

## 执行链

```text
members-v2 validate/load → member alive + devs_online attach
          ↓
extent / btree_ptr / btree_ptr_v2 update
          ↓ transactional runner (sort-order, multi-round, norun skip)
pointer → (dev, offset / bucket_size, remainder)
          ↓ same transaction
alloc(dev,bucket) + backpointer(bucket→owner) + accounting
          ↓
journal/replay primary keys (norun) → rebuild derived trees → validate → publish
```

## 修改边界

| 层 | 责任 | 不包含 |
| --- | --- | --- |
| sb/member + engine attach | 从 members-v2 载入有效 geometry 与 online state，拒绝无 live device 的 physical pointer | allocator/device 管理 API |
| btree types/format | engine-local backpointer tree 与 bcachefs 对应 alloc/backpointer key layout | fs 层 btree-id 编号兼容 |
| update/commit | exact transaction runner、type dispatch、same-transaction derived updates | GC runner |
| interior | 根据上游显式 old/new trigger 边界覆盖 direct bset split/grow pointer writes | 将所有 interior writes 强行改成普通 leaf update |
| journal/recovery | replay primary、rebuild/validate derived state、publication gate | 多版本迁移 |

## 顺序与不变量

- trigger order 沿用本地 `btree_trigger_order()`：alloc 最后、stripes 倒数第二；新
  backpointer tree 不是 trigger source，不能造成循环。
- 对每一个有效 pointer：alloc `(dev,bucket)` 中的 generation/ref 关系与其一致；恰有一个
  backpointer 记载 owner `(btree,level,position,pointer identity)`。
- replace/delete 删除旧关系后增加新关系；两阶段各一次，不重复运行。
- `norun` update 不跑任何 trigger；GC 所有入口保持关闭。
- 任何 recovery crash 点最终以 primary pointer scan 为准；派生集合不一致时不发布。

## 任务处置

T0182 接管 T0183 的功能验收。T0183 保留为已创建的历史 Plan，禁止 dispatch；本任务确认
完成后将其以 absorbed 记录处置，避免重复实现或遗失任务谱系。
