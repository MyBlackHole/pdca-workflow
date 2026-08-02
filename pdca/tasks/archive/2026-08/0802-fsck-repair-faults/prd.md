# T0200 fsck 修复路径故障注入：修复事务中断与落盘失败的恢复验证

## 问题陈述

T0198 实现了 fsck_image(FixErrors::Yes) 修复路径（双向修复 + 每键
单事务 bit_mod_sync + flush_journal 落盘），但其故障行为未验证：
修复事务中途 -12/-4 注入、修复完成后落盘失败（flush_journal 错误）
时 fsck_image 如何失败、镜像如何保持可恢复。T0196 的 recovery-fault-
matrix 模式（RecoveryFaultPoint 三注入点 + 不发布成功断言）已覆盖
恢复路径，本任务以同一模式覆盖修复路径。

## 目标

新增 FsckFaultPoint 注入机制（对齐 RecoveryFaultPoint 的一次性
注入模式），验证：修复事务 restart（-4）下重试成功；修复事务真
OOM（-12 且 restarted==0）硬失败且镜像保持可修复（重跑恢复）；
修复落盘失败（flush 前注入）时未落盘修复被正确丢弃、重跑恢复。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点：修复事务 ENOMEM 语义
      （bch2_trans_commit -ENOMEM → trans restart realloc 重试，
      engine bit_mod_sync 已实现）、fsck 中断可重跑（fsck 幂等）、
      fs.exit() 落盘失败传播（fsck.rs:457-460），与 engine 既有
      -12 重试分支（engine.rs:2128/2173/2586）及 T0196 故障矩阵
      模式（engine.rs:1426/4323）对应。
- [ ] AC-2: FsckFaultPoint 注入机制：私有测试入口 fsck_image_with_
      fault（公开 fsck_image 无参入口不变），DuringRepair /
      AfterRepairBeforeFlush 两注入点；注入路径复用既有 restart/-12
      重试与错误传播语义，无新逻辑分支。
- [ ] AC-3: 修复故障矩阵：restart 注入（-4）下 fsck_image(Yes) 重试
      后成功且镜像修复完整；真 OOM（-12 restarted==0）注入下返回
      Err 且不误报成功；落盘失败注入下返回 Err；所有注入点均
      "不发布虚假成功"（对齐 recovery_fault_matrix_never_publishes_
      success 模式）。
- [ ] AC-4: 恢复验证：真 OOM 与落盘失败中断后重跑 fsck_image(Yes)
      成功（无注入），最终 verify_all 通过、镜像一致；未落盘修复
      被 open_persistent 重建语义正确处理（journal replay 只回放
      已落盘事务）。
- [ ] AC-5: 公开 API 行为不变：fsck_image(path, FixErrors) 签名与
      行为不变（fault=None 路径零改动）；CLI -y 模式不受影响。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过
      一分钟。

## 实现决策

- FsckFaultPoint 枚举（DuringRepair / AfterRepairBeforeFlush），
  一次性注入（对齐 RecoveryFaultPoint：Some(fault) 直接触发，
  engine.rs:1426 模式），私有测试入口 fsck_image_with_fault。
- DuringRepair 注入位置：repair_derived_indexes 的 bit_mod_sync
  事务提交前（engine.rs:2561+ 事务循环），注入 -4（走重试）或
  真 -12（restarted==0 硬失败走错误传播）。
- AfterRepairBeforeFlush 注入位置：fsck_image 的 flush_journal 前
  （engine.rs:2454），注入返回错误（对齐 JournalWrite 注入语义）。
- 测试矩阵沿用 recovery_fault_matrix_never_publishes_success 模式
  （engine.rs:4323）+ 恢复重跑验证（T0198 测试风格）。

## 范围外

修复逻辑本身的新增/改动、fsck 增量修复、多镜像并发 fsck、非
ENOMEM 的错误注入（如 -EIO 已在 T0198 覆盖 Io 错误路径）。

## 备注

前置：T0196（恢复故障矩阵模式）、T0198（修复路径 fsck_image/
repair_derived_indexes/bit_mod_sync）、T0199（并发交错注入模式）
已归档。fsck_image 现签名 engine.rs:2448；bit_mod_sync engine.rs:2555。
