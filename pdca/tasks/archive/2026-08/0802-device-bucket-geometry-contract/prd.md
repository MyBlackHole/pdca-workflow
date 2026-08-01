# T0184 定义设备 bucket 几何与 physical pointer 映射合约

## 问题陈述

- **现状**：subvol 有 `bch_extent_ptr` 的 device、offset、generation 位字段，却没有
  bcachefs `bch_dev.mi.bucket_size` 或由 sector→bucket 得出的持久化位置；因此不能正确维护
  alloc/backpointer。
- **目标**：以本地 bcachefs 为唯一依据，定义单一格式下最小 device geometry、pointer
  offset 到 bucket 的映射、范围检查、持久化和恢复边界，作为合并后的 T0182 的前置。
- **差距**：直接把 offset 当 bucket 会偏离上游 `sector_to_bucket()`/`PTR_BUCKET_POS()`
  语义；直接移植完整 allocator 又超出近期范围。

## 解决方案

从本地 `alloc/buckets.h` 的 `sector_to_bucket()`、`bucket_to_sector()`、
`PTR_BUCKET_POS()` 出发，追踪 `bch_member`/device metadata 的 bucket size 与 bucket count
来源。设计只保留 pointer trigger 与派生索引所必需的 geometry 字段、验证和恢复契约；
不引入空闲选择、LRU、discard 或 GC allocator 策略。

## Seam 分析

### 测试接缝

- 构造不同 bucket size、边界 offset、跨 bucket pointer 与无效 device/generation 的
  geometry/pointer 输入，观察 bucket 位置、长度和拒绝结果。
- 将 geometry 与 journal image/recovery 一起重开，验证 pointer→bucket 结果不变。

### 验收可测性

- 明确的 sector→bucket 商/余数、bucket→sector 逆关系与范围失败信号。
- recovery 前后同一有效 pointer 得到同一 `(device, bucket, bucket_offset)`。

## 用户故事

作为存储引擎维护者，我希望 physical pointer 的 bucket 归属由持久化设备几何决定，
以便随后 alloc/backpointer 更新可复现、可校验且不依赖临时内存约定。

## 实现决策

- 遵循上游 `sector_to_bucket = offset / bucket_size`、`bucket_to_sector = bucket *
  bucket_size` 与 `PTR_BUCKET_POS = (dev, sector_to_bucket(offset))`。
- 仅定义 T0182/T0183 所需的每设备 `bucket_size`、`nr_buckets`、online/generation
  校验与单一格式持久化位置；不实现选择可用 bucket 的 allocator。
- device geometry 与 pointer 不能在恢复后依赖 process-local state；其 journal/superblock
  边界须在设计中明确。

## 测试决策

- 先写纯 geometry 边界单测，再写 journal/recovery 保序测试；保留全量 workspace 与格式
  gate，所有单项在一分钟内。

## 验收标准

- [ ] AC-1: 修改/设计前读取本地 `alloc/buckets.h` pointer→bucket helper、相关 device/member geometry 与 pointer trigger 的范围检查，记录源码锚点。
- [ ] AC-2: 定义最小单一格式 device geometry（bucket size、bucket count、online/generation）及 offset→bucket、bucket→sector、bucket remainder 的精确合约；不把 offset 直接作为 bucket。
- [ ] AC-3: 定义有效/无效 device、越界 bucket、跨 bucket pointer 与 generation 不匹配的错误/恢复行为，并给出可观察不变量。
- [ ] AC-4: 明确 geometry 的持久化与 journal/recovery 顺序，保证恢复前后 pointer→bucket 映射一致，且不依赖完整 allocator/GC。
- [ ] AC-5: 产物可直接解锁 T0182 合并范围；无产品 allocator 实现，定向和全量验证命令均在一分钟内完成。

## 范围外

空闲 bucket 选择、open bucket、LRU/free-index、discard、GC、stripe、设备管理 API 与
完整 bcachefs superblock 兼容。

## 备注

前置：T0181；后续：T0182（已吸收原 T0183 的派生写入/恢复范围）。
