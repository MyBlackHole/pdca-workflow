# T0188 桶分配回收公开 API 端到端与属性测试

## 问题陈述

T0187 已实现最小 bucket candidate、占用、回收、generation、freespace、backpointer 与
recovery 链路，但主要证据集中在底层 transaction 测试。公开 API 的多桶选择、失败原子性、
重启边界和长期操作序列还缺少独立模型验证。

## 目标

建立公开 `allocate_bucket` / `reclaim_bucket` 的端到端测试夹具与属性模型，验证 alloc、
freespace、backpointer 和 generation 集合在正常、失败、重启及事务重试下保持一致。

## 验收标准

- [ ] AC-1: 公开 API 在 members-v2 geometry 下 deterministic 选择 candidate，覆盖多桶、first_bucket 和 nbuckets 边界。
- [ ] AC-2: allocate→pointer 使用→回收→generation 复用的端到端序列与独立模型一致。
- [ ] AC-3: live backpointer、dirty/cached sector、stale generation、非法设备和越界 bucket 被拒绝且无半状态。
- [ ] AC-4: journal durable/replay、process-style restart、ENOMEM/restart fault 后 alloc/freespace/backpointer 集合一致。
- [ ] AC-5: 属性测试生成有限 bucket/pointer 操作序列，失败操作不改变模型与持久状态。
- [ ] AC-6: 定向测试、属性测试、workspace 全量测试、fmt 和 diff gate 全部通过；单项不超过一分钟。

## 实现决策

- 只扩展测试夹具与必要的可观测性，不重写 T0187 allocator/reclaim 语义。
- 独立模型只记录 bucket 状态、generation、live reference 和 freespace membership，不引入第二套存储格式。
- 故障注入复用现有 transaction/journal/recovery fault points。

## 范围外

完整 discard worker、open-bucket GC、后台 GC/LRU、stripe/EC、VFS、旧格式迁移和多格式兼容。

## 备注

前置：T0187 已归档并通过 Check/Act/Archive。
