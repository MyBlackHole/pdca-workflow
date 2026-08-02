# T0183 实现 alloc/backpointer 派生维护与崩溃恢复验证

## 问题陈述

T0180 已确认 bcachefs pointer trigger 在同一事务中更新 alloc 并写 backpointer；
subvol 当前没有等价 bucket 或反向桶维护。T0181 的合约与 T0182 的 runner/dispatch
均为前置。

## 目标

实现最小 physical pointer 增删到 alloc/backpointer 的同事务派生更新、验证路径和
崩溃恢复不变量；严格限定在 T0181 已定义的单一格式、非 GC 范围。

## 验收标准

- [ ] AC-1: 开始修改前逐段读取本地 `alloc/buckets.c` pointer/extent trigger、`alloc/background.c` alloc trigger、`alloc/backpointers.c` writer/validator，记录等价语义锚点。
- [ ] AC-2: pointer 插入、覆盖和删除在同一事务中维护 T0181 定义的 alloc 与 backpointer；不会留下重复、悬挂或漏记的反向桶记录。
- [ ] AC-3: journal/recovery 按 T0181 合约重建或受控维护派生状态，故障注入覆盖主键与派生键之间的关键 crash 点。
- [ ] AC-4: 有确定性验证器从主 pointer 集合比对 alloc/backpointer，且测试涵盖 btree pointer 与 extent 两种来源。
- [ ] AC-5: 定向、故障/属性和全量 workspace 测试通过，单项不超过一分钟。

## 范围外

GC trigger、完整 bucket LRU/free-index 策略、stripe-backpointer 和完整 fsck。

## 备注

前置：T0181、T0182 完成并确认。
