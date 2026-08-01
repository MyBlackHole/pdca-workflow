# T0181 定义物理 pointer、alloc/backpointer 与恢复的最小持久化合约

## 问题陈述

T0180 已证实 bcachefs 的 extent 与内部 btree pointer 变更会派生 alloc、
backpointer、accounting/reconcile 更新；subvol 尚无物理 bucket 数据模型。若先实现
runner，会没有可验证的主数据/派生数据边界和 `BTREE_TRIGGER_norun` replay 的恢复语义。

## 目标

仅定义 subvol 单一格式下最小 physical-pointer、alloc 与 backpointer btree 的数据、
持久化和恢复合约，明确哪些状态可由主键重建及何时重建；不实现产品路径。

## 解决方案

把带有效物理 pointer 的 `extent`、`btree_ptr` 和 `btree_ptr_v2` 视为唯一主数据；
alloc、backpointer 与 accounting 是可验证的派生状态。恢复先按现有 journal 语义恢复主
btree，再运行显式派生状态扫描/重建，不让 `BTREE_TRIGGER_norun` 隐式承担维护责任。设计
只定义逻辑树职责和不变量；具体 Rust 模块、byte layout、btree id 与写入实现留给后续已
拆分任务。

## Seam 分析

### 测试接缝

- 恢复后扫描主 pointer btree，独立生成期望的 alloc/backpointer 集合，再与派生树比较。
- 在主 pointer journal 持久化前、持久化后而派生索引尚未可见、以及重放/重建完成后三个
  边界注入故障；观察恢复后主键和派生索引的不变量。
- 不 mock bcachefs；使用 subvol 现有 journal image/recovery、transaction restart 和
  btree split 测试接缝。

### 验收可测性

- 每个主 pointer 必须产生唯一的 alloc bucket 归属和反向记录；派生键不能指向不存在或
  不匹配的主 pointer。
- `norun` replay 后的显式重建必须使扫描得到的期望集合与派生集合一致。
- 设计本身无产品代码；文档检视、workflow 校验和既有定向/full test 是 pass/fail 信号。

## 用户故事

作为存储引擎维护者，我希望 physical pointer 的主从状态和恢复顺序在实现前固定下来，
以便后续 transaction runner 不会将可恢复的数据写成不可校验的 alloc/backpointer 状态。

## 实现决策

- 主数据为含有效物理设备/bucket pointer 的 extent 与内部 btree pointer；内存 `mem_ptr`
  不是物理所有权证据。
- 使用逻辑 `alloc` 与 `backpointers` 树职责，不复用 bcachefs fs 层编号；它们的 key/value
  字段语义、生成代与主 pointer 身份须有本地 bcachefs 对照依据。
- `alloc` 是每 device/bucket 的派生使用状态；`backpointer` 以 bucket 与主 pointer 身份
  反向定位。删除/覆盖必须移除旧派生关系后加入新关系，保持同一 transaction 可观察边界。
- accounting 仅作为可从主 pointer 重算的派生值纳入合约；在未定义完整 upstream accounting
  数据模型前不暴露其值或写入占位格式。
- 现阶段只定义非 EC、非 stripe 最小合约；stripe-backpointer、LRU/free-index、完整 GC
  继续显式排除，不能用空结构假装实现。
- recovery 以主 pointer 为准：先完成现有 main-key replay，再丢弃/忽略待重建派生状态并
  通过确定性扫描重建；只有重建完成后才允许公开 alloc/backpointer 查询。

## 测试决策

- T0182 为 runner 顺序、multi-round 与 pointer dispatch 添加确定性测试。
- T0183 为主 pointer→派生状态的集合等价、覆盖/删除、split、journal/replay 与 crash 点
  添加确定性和故障/属性测试。
- T0181 仅验证设计锚点、任务依赖和现有恢复基线；所有命令保持一分钟内。

## 验收标准

- [ ] AC-1: 修改/设计前逐段读取本地 bcachefs `data/extents.h`、`alloc/buckets.c`、`alloc/backpointers.c` 和 journal/recovery 对应源码，并记录源码锚点。
- [ ] AC-2: 定义 extent/btree pointer、alloc bucket、backpointer/stripe-backpointer、accounting 的最小主从关系、键位置与单一格式持久化边界；不采用 bcachefs fs 层 btree-id 编号。
- [ ] AC-3: 明确 journal replay 使用 `norun` 时的派生状态恢复方案，并给出 crash 点与可观察不变量。
- [ ] AC-4: 设计文档区分可在本项目实现的最小合约与依赖完整 GC/stripe 的范围外项，不能以占位逻辑替代上游语义。
- [ ] AC-5: 设计结论可直接作为 T0182/T0183 的输入；无产品代码变更，验证命令在一分钟内完成。

## 范围外

实现 trigger runner、alloc/backpointer 写入、完整 GC、stripe 与 VFS 层。

## 备注

前置：T0180；后续：T0182、T0183。
