# T0200 Triage Brief：fsck 修复路径故障注入

## 任务概述

T0198 修复路径（fsck_image Yes 模式：双向修复 + 每键单事务 +
flush 落盘）已完成，但故障行为未验证。以 T0196 恢复故障矩阵
（RecoveryFaultPoint 三注入点）同一模式覆盖修复路径：修复事务
中断（-4 restart / 真 -12 OOM）与落盘失败（flush 前注入）下的
失败语义与恢复能力。

## 上游锚点（已核对）

- 修复事务 ENOMEM：bch2_trans_commit -ENOMEM → trans restart
  （realloc 扩容重试）；engine 既有 `-12 && (realloc_bytes_required
  != 0 || restarted != 0)` 重试分支（engine.rs:886/1090/1633-1643/
  2128/2173/2586）——真 OOM（restarted==0）硬失败传播。
- fsck 中断可重跑：上游 fsck 幂等（每次重跑重新扫描修复）；
  engine 修复从 alloc 树派生期望集（engine.rs:2476-2498），重跑
  语义天然成立。
- 落盘失败传播：上游 fs.exit()（fsck.rs:457-460）失败 → fsck
  返回错误；engine flush_journal 错误传播（engine.rs:2454）。
- T0196 矩阵模式：RecoveryFaultPoint 一次性注入 + 不发布虚假成功
  断言（engine.rs:1426/4323-4341）。

## 方案

1. FsckFaultPoint 枚举：DuringRepair / AfterRepairBeforeFlush，
   一次性注入（Some(fault) 触发），对齐 RecoveryFaultPoint 模式。
2. 私有测试入口 fsck_image_with_fault(path, fix, fault)：
   - DuringRepair：bit_mod_sync 事务提交前注入 -4（走重试）或
     真 -12（restarted==0，硬失败错误传播）
   - AfterRepairBeforeFlush：flush_journal 前注入错误
   - 公开 fsck_image 调用 fault=None（零行为改动）
3. 测试矩阵：
   - restart 注入 → Yes 重试成功 + 修复完整
   - 真 OOM 注入 → Err 不误报 → 重跑无注入成功
   - 落盘失败注入 → Err 不误报 → 重跑成功（未落盘修复被重建
     语义处理）
   - 全注入点不发布虚假成功（对齐 4323 模式）

## 风险

- DuringRepair 一次性注入落在哪个 bit_mod_sync 不确定（修复多个
  键时第一个命中）——无碍：任一事务中断/失败都验证目标语义。
- 真 -12 注入与 realloc 路径交互：注入点直接返回 -12 且
  restarted==0 → 走硬失败分支（不经重试）→ 语义精确。
- 落盘失败后重跑的"未落盘修复被丢弃"依赖 journal replay 只回放
  已落盘事务（open_persistent 语义，T0195 已验证）——重跑由
  open_persistent 重建派生态 + 重新修复完成，需实测确认。

## 建议

按上述方案立项；AC-1 锚点、AC-2 注入机制、AC-3 故障矩阵、AC-4
恢复验证、AC-5 API 不变、AC-6 全绿。
