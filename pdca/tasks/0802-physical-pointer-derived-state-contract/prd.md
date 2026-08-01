# T0181 定义物理 pointer、alloc/backpointer 与恢复的最小持久化合约

## 问题陈述

T0180 已证实 bcachefs 的 extent 与内部 btree pointer 变更会派生 alloc、
backpointer、accounting/reconcile 更新；subvol 尚无物理 bucket 数据模型。若先实现
runner，会没有可验证的主数据/派生数据边界和 `BTREE_TRIGGER_norun` replay 的恢复语义。

## 目标

仅定义 subvol 单一格式下最小 physical-pointer、alloc 与 backpointer btree 的数据、
持久化和恢复合约，明确哪些状态可由主键重建及何时重建；不实现产品路径。

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
