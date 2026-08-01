---
schema: pdca.asset/v1
id: T0184-0802-device-bucket-geometry-contract
phase: check
source_ids: [evt-001, evt-002]
---

## 上下文

合并 T0182/T0183 后发现 alloc/backpointer 的 bucket 位置不能由裸 pointer offset 猜测。T0184
核对本地 bcachefs 的 geometry helper 和 subvol 当前 superblock/member 实现。

## 假设与结果

| 假设 | 结果 | 证据 |
| --- | --- | --- |
| subvol 缺少任何可持久化的 bucket geometry | 不成立；members-v2 已持久化 `nbuckets`、`first_bucket`、`bucket_size` | evt-001 |
| offset 可直接作为 bucket | 不成立；上游以 `offset / bucket_size` 与 remainder 映射 | evt-001 |
| 现有 member geometry 已可直接接受 physical pointer | 不成立；member-live identity 与 `devs_online` attach 尚未接入该路径 | evt-001 |
| superblock/recovery 接缝稳定 | 成立；成员校验、备份 superblock recovery 与全量测试通过 | evt-002 |

## 分析

权威 geometry 是持久化 members-v2。对有效 pointer，bucket 为 `offset / bucket_size`，
bucket offset 为余数，alloc/backpointer 的 bucket 位置为 `(dev, bucket)`；bucket 必须位于
`[first_bucket, nbuckets)`。mapping 的前置包括 member alive、device online 与 generation
相符。插入无效 pointer 必须拒绝，删除无效 pointer 不得创建新的派生状态。

当前 persistent journal 已写 members-v2 geometry，但其 member 默认 UUID 和 runtime online
mask 尚未形成 physical-pointer attach 语义。T0182 必须补上该 bridge，并在 replay/scan 前
载入验证后的 geometry。无需创建新 on-disk geometry 格式、allocator 或 GC。

## 失败原因

不适用：设计验收满足。发现的是后续实现前置缺口，而不是当前 cookie API 的数据损坏。

## 适用边界

仅适用于 future physical pointer 的 bucket 归属与派生索引；不覆盖可用 bucket 选择、LRU、
discard、GC、stripe 或完整多设备管理。

## 下一轮建议

确认后重写 T0182 完整 Plan：吸收原 T0183 的 derived writer/rebuild 范围，并纳入
members-v2 live/online attach、准确 bucket mapping、transaction runner 和 crash recovery。
