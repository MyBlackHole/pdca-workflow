# T0187 实现桶分配回收与反向引用 bucket btree 完整链路

## 问题陈述

当前 subvol 已有 physical pointer 到 alloc/backpointer 的事务派生维护、恢复重建和一致性校验，
但尚无真正的 bucket candidate 分配、占用、释放、generation 复用与回收状态机。因此“桶分配—
使用—回收—复用—反向引用校验”仍未闭合。

本任务仅依据本地 bcachefs：`fs/alloc/buckets.c` 的 bucket ref/update 与 pointer trigger、
`fs/alloc/background.c` 的 alloc key 状态转换、`fs/alloc/backpointers.c` 的 bucket mismatch
和双向检查、`fs/alloc/discard.c` 的回收前置条件，以及 `fs/init/recovery.c` 的 alloc recovery
passes。不得引入外部版本语义。

## 目标

1. 建立最小 bucket allocation candidate、占用和释放状态机，严格绑定 members-v2 geometry。
2. 在同一 transaction 中维护 alloc bucket 状态与 backpointer bucket btree。
3. 实现 generation 校验、释放后复用边界和 recovery rebuild/校验。
4. 通过审计、故障注入和属性测试证明 bucket 状态、primary pointer 与反向引用一致。

## 验收标准

- [ ] AC-1: 修改前逐段读取并记录本地 `buckets.c`、`background.c`、`backpointers.c`、
  `discard.c`、`init/recovery.c` 的分配、释放、generation、mismatch 和错误分支；每个 Rust
  状态转移有源码锚点。
- [ ] AC-2: 在 members-v2 geometry 下实现 deterministic bucket candidate 选择、占用和释放；
  offline/dead/zero-size/越界 bucket 必须拒绝且不产生半状态。
- [ ] AC-3: bucket 占用、pointer insert/overwrite/delete、释放和 generation 复用在同一
  transaction 更新 alloc 与 backpointer bucket btree；不得出现重复、悬挂或漏记。
- [ ] AC-4: 仅当 bucket 无 live dirty/reference、未 open、generation 匹配且回收前置条件满足
  时才允许 reclaim；reclaim 后复用必须拒绝 stale-generation pointer。
- [ ] AC-5: journal replay、rebuild、故障/重启后，primary pointer、alloc bucket、backpointer
  bucket btree 和 generation 集合一致；校验失败不得发布成功状态。
- [ ] AC-6: deterministic、故障注入、属性、全量 workspace、fmt 和 diff gate 全部通过；每项
  测试不超过一分钟。

## 实现决策

- 复用 T0182/T0185/T0186 的 pointer trigger、members-v2 geometry、derived validator 和
  recovery fault 入口，不创建第二套 backpointer 格式。
- bucket 状态字段与 generation 必须逐字段对照本地 `bch_alloc_v4`、bucket helper 和
  `bch_backpointer`；错误处理沿用本地拒绝/重试边界。
- 本任务实现最小可验证 allocator/reclaim 核心，不扩展完整 GC、stripe/EC、LRU/discard
  worker 或 VFS。

## 测试决策

- 先测试单 bucket candidate→use→release→reuse，再覆盖多 pointer、overwrite/delete 和
  stale generation。
- 对 journal durable、reclaim 前、reclaim 后、reuse 前后注入 restart/fault。
- 属性测试生成 bucket/pointer 操作序列，以独立模型比较 alloc、backpointer 和 generation。

## 范围外

完整后台 GC、open bucket worker、LRU/discard worker、stripe/EC、完整 fsck、VFS、旧格式迁移和
多格式兼容。

## 备注

前置：T0182、T0185、T0186 已完成并归档。本任务是用户明确扩展的 allocator/reclaim 核心，
仍保持单一格式和本地 bcachefs 语义对照。
