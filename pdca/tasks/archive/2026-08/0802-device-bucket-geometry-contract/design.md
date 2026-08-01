# T0184 device bucket geometry 合约

## 事实锚点

- 本地 bcachefs `alloc/buckets.h:18-39,116-132` 定义
  `bucket = offset / bucket_size`、`bucket_offset = offset % bucket_size`、
  `PTR_BUCKET_POS = (ptr.dev, bucket)`；`bucket_to_sector = bucket * bucket_size`。
- `alloc/buckets.c:672-678` 在插入 pointer 时拒绝无效 bucket，删除无效 pointer 则不创建
  新状态。
- subvol `sb/mod.rs:37-63,93-135` 已有与本地格式对应的 `bch_member`/
  `bch_member_cpu`：`nbuckets`、`first_bucket`、`bucket_size`、`valid`。
- `engine.rs:1271-1300` 将单设备 members-v2 写入持久化 superblock；`sb/io.rs:273-365`
  在读取时按成员数、bucket range 和 size 进行验证。

## 合约

对 physical pointer `p`，只在以下前提同时成立时允许进入 T0182 的 transactional
pointer trigger：

1. `p.dev < sb.nr_devices`，该 members-v2 record 存在且 `bch2_member_alive()` 为真；
2. `bch2_dev_idx_is_online(c, p.dev)` 为真；
3. `bucket_size > 0`，令 `bucket = p.offset / bucket_size`，
   `bucket_offset = p.offset % bucket_size`；
4. `first_bucket <= bucket < nbuckets`；
5. pointer generation 与 T0182 将维护的 alloc generation 相符。

映射是 `bucket_to_sector(bucket) = bucket * bucket_size`。它不是把 offset 本身当作
bucket，也不以 process-local state 决定 bucket。alloc key 的位置是 `(p.dev, bucket)`；
backpointer 的 bucket 组成部分也必须使用该位置。

## 恢复与错误边界

members-v2 与 journal metadata 同属持久化 superblock，故 recovery 应先验证并载入
members-v2，建立 online-device mask，随后才 replay/scan physical pointer。恢复前后读取同一
member geometry 必须产生同一 `(dev, bucket, bucket_offset)`。

插入时无效 device、offline/dead member、零 bucket size、bucket 越界或 generation 不匹配
是错误；不得创建 alloc/backpointer。删除时无法解析的旧 pointer 不能制造新派生状态，
但其报错/忽略分支必须沿用本地 trigger 的 insert-vs-delete 边界并由 T0182 测试。

## 当前缺口与交接

geometry 字段已存在，不需要新 on-disk format；当前缺口是：persistent journal 初始化写入
的 member 仍为默认 UUID，且没有把 members-v2 的 live state 建入 `devs_online`。因此 T0182
必须在 physical pointer 接口启用前完成 member identity/online attach/recovery，并测试恢复后
映射稳定。这不是 allocator、GC 或 LRU 实现。
