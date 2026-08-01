# T0182 实现 transaction trigger runner 与 pointer/extent dispatch

## 问题陈述

subvol commit 当前只运行 snapshot memory trigger，未具备 bcachefs transaction trigger
的 sort-order、多轮追加 update 与 insert/overwrite 状态语义；extent/btree pointer
类型也未分派。T0181 的物理状态合约是本任务前置。

## 目标

在 T0181 确认的最小类型范围内，对照本地 `fs/btree/commit.c` 与 `types.h` 实现
transaction trigger runner 及 extent/btree pointer dispatch；同时证明 btree split 的
最终持久化 pointer 路径是否进入该 runner。

## 验收标准

- [ ] AC-1: 开始修改前逐段读取本地 `fs/btree/commit.c` runner、`types.h` trigger mask 与 `data/extents.h` trigger 绑定；执行顺序、多轮与错误分支有源码锚点。
- [ ] AC-2: 在 T0181 定义的类型范围内，runner 按 sort-order 运行并处理 trigger 追加的 update；insert/overwrite 触发状态不得重复运行。
- [ ] AC-3: extent、btree_ptr 与 btree_ptr_v2 均按上游语义分派；internal split/grow 的实际持久化路径有确定性测试。
- [ ] AC-4: `norun` 保持显式且不会误当作派生状态已维护；不得启用 GC runner。
- [ ] AC-5: 定向、故障/属性和全量 workspace 测试通过，单项不超过一分钟。

## 范围外

alloc/backpointer 派生写入（T0183）、GC、stripe 和完整 device allocator。

## 备注

前置：T0181 完成并确认合约；后续：T0183。
