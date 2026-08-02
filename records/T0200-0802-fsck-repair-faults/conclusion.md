# T0200 结论

## 任务结果

T0200 已完成并确认（V-T0200-001 confirmed）：fsck 修复路径的故障
注入与恢复验证全部通过。

## 交付物

- subvol `f404fec`：engine.rs +173/-8
  - `FsckFaultPoint` 枚举：DuringRepairRestart（提交前注入 -4）、
    DuringRepairOom（硬 -12，restarted==0）、AfterRepairBeforeFlush
    （flush 前注入失败）
  - `fsck_image_with_fault` 私有测试入口，公开 `fsck_image` 零改动
  - `bit_mod_sync` 补 -4 重试分支（T0198 缺口，对齐 lockrestart_do
    iter.h:1115-1127）
  - 4 个测试：restart 重试收敛 / OOM 中止+重跑恢复 / flush 失败
    中止+重跑恢复 / 故障矩阵不发布虚假成功

## 关键结论

1. **修复事务 restart 语义**：上游 trans restart（-4）必须重试而非
   中止（lockrestart_do iter.h:1115-1127）；T0198 的 bit_mod_sync
   缺 -4 分支是真实缺口，已修复并逐字对齐 reclaim/allocate 既有模式。
2. **真 OOM 注入语义**：-12 且 realloc_bytes_required==0（restarted
   ==0）走既有错误传播中止，不误入重试循环。
3. **落盘失败恢复**：修复提交但 flush 失败（fs.exit() 失败镜像，
   fsck.rs:457-460）→ Journal 错误不误报成功；重跑时未落盘修复被
   journal replay 丢弃（只回放已落盘事务），open_persistent 重建
   派生态后重新修复收敛——实测确认。
4. **fault 一次性消费**：&mut Option 透传，首个修复事务吞掉注入，
   后续事务不受影响（对齐 RecoveryFaultPoint 模式）。

## 数值

- 全量 243 测试全绿（228 lib + 10 proptest + 5 fsck_cli）
- proptest 单项 39.92s ≤ 1min（AC-6 门禁）
- cargo fmt --check 通过

## 遗留

- T0199 归档时的注入点错位缺陷已在本任务前置修复（subvol `733b2fe`，
  DiscardCommitRestart 归位 reclaim_bucket）——T0200 无需再处理。
- 模型 op 域扩展、持久化并发交错留待后续任务（T0200 disposition
  projected）。
