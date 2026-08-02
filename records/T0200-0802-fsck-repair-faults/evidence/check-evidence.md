# T0200 check 阶段：AC 验收证据

## 实现清单

- subvol `f404fec`：engine.rs +173/-8
  - `FsckFaultPoint` 枚举（DuringRepairRestart / DuringRepairOom / AfterRepairBeforeFlush）
  - `fsck_image_with_fault` 私有测试入口（公开 `fsck_image` 调它传 None，零改动）
  - `repair_derived_indexes` 增加 fault 参数，透传 `&mut Option<FsckFaultPoint>`（一次性消费）
  - `bit_mod_sync` 注入位点（事务提交前，对齐 trans_maybe_inject_restart commit.c:1390）+ 补 -4 重试分支
  - 4 个测试

## 上游锚点（AC-1）

- trans_maybe_inject_restart 在 `__bch2_trans_commit` 内提交前调用：fs/btree/commit.c:1390
- lockrestart_do 对 transaction_restart 循环重试：fs/btree/iter.h:1115-1127
- delete_freespace_key 单事务提交（repair 事务形态）：fs/alloc/check.c:366-371
- fs.exit() 落盘失败传播：fs/fs/fsck.rs:457-460（T0198 已锚定）
- 硬 -12 中止语义：engine.rs 既有 `-12 && realloc_bytes_required != 0` 重试条件，
  restarted==0 走错误传播（engine.rs:886/1090 既有分支）

## AC 对照

| AC | 验收 | 证据 |
|----|------|------|
| AC-1 | 修改前锚点记录 | ac1-source-anchors.md |
| AC-2 | FsckFaultPoint 注入机制 | fsck_repair_restart_injected_retries_and_succeeds（-4 重试收敛，消费一次）|
| AC-3 | 故障矩阵不发布虚假成功 | fsck_repair_fault_matrix_never_falsely_reports_success（OOM/Flush 均 Err）|
| AC-4 | 中断后重跑恢复 + verify 通过 | fsck_repair_oom_injected_aborts_and_rerun_recovers、fsck_repair_flush_failure_injected_aborts_and_rerun_recovers（重跑后 open_persistent verify_all Ok）|
| AC-5 | 公开 fsck_image 不变 | 公开入口签名不变，fault=None 路径与 T0198 原实现逐字等价；fsck_cli 5 测试全绿 |
| AC-6 | 全量门禁 | 228 lib + 10 proptest + 5 cli 全绿；proptest 39.92s ≤1min；fmt --check 通过 |

## 结论

待 verdict 确认。
