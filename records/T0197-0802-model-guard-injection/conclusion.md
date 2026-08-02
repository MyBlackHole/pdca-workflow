# T0197 结论

## 概述

属性测试模型状态机注入守卫决策：`open_bucket_discard_model_protects_
open_from_reuse` 模型删除手写守卫预判（op 5/6 无条件尝试 open/close），
新增 op 7 set_device_rw 覆盖 not_rw 维度，合法/非法期望由实现
verify_all / verify_guard_invariants 裁决并匹配错误名
（OpenBucketFree / NotRwBucketFree，open 树序优先于 not_rw）。
模型从"预判合法"转为"探索含非法在内的操作并由实现裁决"。

## 验证

- proptest 随机序列（op 域 0..8，16 cases × 1..=40 ops）：每步 alloc
  树投影断言 + verify_all / verify_guard_invariants 双裁决 + 全操作
  路径 expect_verdict 匹配。
- 确定性 not_rw 场景 `not_rw_dimension_guard_verdicts_are_
  implementation_adjudicated`：NotRwBucketFree / open 优先 / open 拒绝
  set false -16 / not_rw allocate is_err / reclaim -16 / worker EAGAIN
  旋转 / reopen 后 rw_devs 重建再分配成功。
- 3 个模型 bug 由最小反例定位修复（op 5 影子数组漏更新、op 3 错误清
  open、worker 缺 device_rw 条件），proptest-regressions 自动保存 4 个
  反例重放回归。
- workspace 全绿：216 lib + 10 btree_proptest + 3 fsck_cli = 229，单项
  ≤40s（btree_proptest 38.84s ≤ 1min）；fmt 通过；提交 2873d52
  （engine.rs +242/-35 全在 mod tests、proptest-regressions +3），
  生产代码零改动。
- 双轴审查：0 blocking / 0 MEDIUM / 0 LOW。

## 边界与发现

- 引擎语义被反例确认：open_bucket 是无预校验 insert（engine.rs:901），
  allocate_bucket 不检查 open_buckets——open 与 data_type 是独立维度，
  模型最初假设互斥是错误；open∧free 桶可被后续 allocate 命中，reclaim
  才报 -16（open 守卫先于 rw 检查）。
- set_device_rw(false) 以"open 桶存在即 -16"表达
  bch2_dev_allocator_remove 等待 open write points 排空的语义
  （background.c:1690-1722）；reopen 后 rw_devs 从 devs_online 重建
  （engine.rs:1687-1700），模型需同步重置。
- ModelEngine（Option 包装 + Drop 关桶）保证 proptest 失败时
  open-bucket-leak 断言（engine.rs:1788）不掩盖真实失败消息。
- 断言形态沿用 expect_verdict（失败先关桶再 panic），库 API 零变化
  （约束 8：上游无模型裁决函数，裁决逻辑全部复用既有 verify 系列）。

## 建议链（下一轮）

1. fsck 修复路径：`subvol-fsck -f` 修复模式（对齐 bcachefs fsck 的
   repair 语义），与既有只读 verify_all 形成对照。
2. loom 风格并发交错：worker/discard/reclaim 在并发下的事务级验证
   （现有并发测试为端到端级）。
3. 模型状态机扩展到 alloc 树多桶操作组合的深度随机序列（op 域扩大、
   case 数提升），并纳入 CI 定时全量。
