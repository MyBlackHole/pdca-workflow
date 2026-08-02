# T0195 结论

## 概述

fsck 风格 CLI 健康检查入口：lib 新增 `fsck_image(path)`（打开持久化引擎 +
运行 verify_all，语义锚点 fsck.rs:419-447 打开→全量 pass→首错退出），
bin/subvol-fsck 手写参数解析（-n/--no-repair、-f/--force、-h），退出码
0=通过（stdout "OK"）/1=校验失败（stderr "ERROR: {error}"）/2=打开-IO
错误（stderr "cannot open {path}: {错误名}"），仅 no-repair 模式（对齐
上游 -n `fix_errors=no`，fsck.rs:266-269）。

## 验证

- workspace 全绿：213 lib + 10 btree_proptest + 3 fsck_cli = 226，单项 ≤40s（≤1min）
- fmt 通过；提交 fb9e85a（+179/-3，4 files）
- 双轴审查：0 blocking / 0 MEDIUM / 0 LOW

## 边界与发现

- 实现期发现（round 3 澄清）：open_persistent 打开时总执行
  rebuild_derived_state（engine.rs:1716，对齐上游恢复语义），预置索引
  不一致会被打开流程修复；故 CLI 的损坏场景体现为打开失败（Io 错误名 +
  exit 2），索引不一致校验失败路径（OpenBucketFree/NeedDiscardSet 错误名）
  由库级 verify_all 测试覆盖。AC-4 两种错误名路径均已验证。
- 库 API 仅新增 fsck_image；verify_all 与既有 API 行为不变（AC-5）。
- 残留：lib 既有 never-used 警告（非本次引入）。

## 下一轮建议

1. verify_all 作为 worker 变体最终一致性检查点（T0191 建议延续）。
2. 属性测试模型状态机注入守卫决策（T0193 建议延续）。
3. -f/--force 当前仅接受；若未来实现 fix 路径可对齐 upstream repair 语义。
