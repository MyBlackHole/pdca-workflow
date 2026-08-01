# T0182 实现 transaction trigger、alloc/backpointer 派生维护与恢复

## 问题陈述

- **现状**：subvol commit 当前只运行 snapshot memory trigger，未具备 bcachefs transaction
  trigger 的 sort-order、多轮追加 update 与 insert/overwrite 状态语义；extent/btree pointer
  类型也未分派。members-v2 已持久化 bucket geometry，但尚未建立 member-live/online attach。
- **目标**：在单一格式下实现 physical pointer 的 transaction trigger、alloc/backpointer
  派生维护、rebuild/recovery 与验证；不实现 allocator/GC。
- **差距**：若只移植 runner，无法端到端证明 multi-round；若只写派生树，则缺少精确
  bucket mapping、`norun` recovery 和 split pointer 的持久化 trigger 边界。

## 目标

以 T0181/T0184 为前置，完整交付四段同一事务链：

1. 从 members-v2 attach 可用 device geometry 并建立 online mask；
2. 对照 `commit.c` 运行 transactional trigger 的 sort-order、多轮、insert/overwrite
   状态机，且保留 `norun`；
3. 为 extent、`btree_ptr`、`btree_ptr_v2` 分派 pointer trigger，按
   `(dev, offset / bucket_size)` 更新 alloc 与 backpointer；
4. recovery 先 replay 主 pointer，再 deterministic rebuild/validate 派生树，完成前不发布。

## 验收标准

- [ ] AC-1: 修改前逐段读取本地 `commit.c` runner、`types.h` trigger/order、`data/extents.h` binding、`alloc/buckets.{h,c}`、`alloc/backpointers.c`、`init/recovery.c` 与 device member 代码；每个执行/错误分支有源码锚点。
- [ ] AC-2: members-v2 geometry 建立 member-alive/devs_online attach；有效 pointer 精确按 `offset / bucket_size` 映射，offline/dead/zero-size/越界/generation-mismatch pointer 在 insert 时失败且不产生派生状态。
- [ ] AC-3: runner 按上游 sort-order 多轮处理 trigger 追加的 update；insert/overwrite 只各运行一次，`norun` 全程不运行，GC runner 不被启用。
- [ ] AC-4: extent、btree_ptr、btree_ptr_v2 均分派到 pointer trigger；每个有效 pointer 在同一事务更新 alloc 与 backpointer，replace/delete 无重复、悬挂或漏记；split/grow 的实际持久化路径有确定性覆盖。
- [ ] AC-5: recovery 先 replay 主 pointer，再重建/校验派生树；主 pointer durable 而派生更新中断、journal replay、split 与 fault/restart 后，派生集合等于主 pointer 扫描结果且未提前发布。
- [ ] AC-6: 定向、故障/属性、全量 workspace 和格式测试通过；每项单测不超过一分钟。

## Seam 分析

### 测试接缝

- raw extent transaction：构造 valid/invalid pointer，观察同一 commit 中的 alloc/backpointer
  keys、runner flags 和 journal records。
- internal split/grow：在实际 parent/root pointer write 边界验证 trigger，不仅测试 leaf
  update list。
- recovery：在主 pointer journal durable、派生 update 前后注入 restart/fault，重开后以
  独立主 pointer 扫描对比派生集合。

### 验收可测性

- 以 members-v2 geometry 导出的 `(dev,bucket,remainder)`、trigger run flags、alloc/
  backpointer 集合及 recovery publication state 作为 pass/fail 信号。
- 任一无效 pointer 不能产生可观察的 alloc/backpointer key；任何 mismatch 必须使验证失败。

## 用户故事

作为存储引擎维护者，我希望 physical pointer 的主键、bucket geometry、派生索引和恢复在
同一 transaction 合约中闭合，以便崩溃后既不会丢失空间使用记录，也不会把不一致索引发布
给分配逻辑。

## 实现决策

- 采用 T0184 的 members-v2 geometry，不创建新 geometry 数据格式；physical pointer 启用前
  建立 member identity 与 `devs_online` attach/recovery。
- alloc 使用既有 local btree id 4；新增 engine-local backpointer btree id，不要求 bcachefs
  fs 层编号一致。其 key/value layout、generation 与 owner identity 必须逐字段对照本地
  `bch_alloc_v4`/`bch_backpointer`。
- runner 严格复刻 `commit.c` 的 sort-order、多轮、同 trigger insert/overwrite 合并与
  `BTREE_TRIGGER_norun` 跳过条件；不接入 `gc_visited` 或 GC runner。
- interior split/grow 采用上游 `interior.c` 的显式 old/new trigger 边界；不得假设直接
  bset 写入自动经过 transaction runner。
- recovery 遵循 T0181：主 pointer replay 后显式 rebuild/validate 派生树，完成前禁止
  alloc/backpointer 查询或基于它们分配。

## 测试决策

- 先添加 geometry/member attach 和 runner 状态机的确定性测试；再添加 pointer insert/
  replace/delete、split/grow 和 recovery/fault/property tests。
- 每次产品改动前读取对应本地 bcachefs 源；最终运行全量 workspace 与 fmt gate。

## 范围外

完整 device allocator、open bucket、LRU/free-index、discard、GC、stripe/EC、完整 fsck、
VFS 与多格式迁移。

## 备注

前置：T0181、T0184。T0182 吸收原 T0183 的 alloc/backpointer/recovery 范围；T0183 不得
单独进入 Do，待本任务完成后以“已吸收”处置。
