# T0201 check 阶段：AC 验收证据

## 实现清单

- subvol `c571798`：engine.rs +128（T0201 主体）
  - `concurrent_crash_child(engine: Arc<StorageEngine>, mode)`：4 写者线程（btree put +
    allocate/reclaim 双回收）× Barrier(5)（4 写者+主线程全程参与，T0199 规则）+ 一次性
    TransactionRestart 注入；三分支崩溃点：cc-flush-before（写者完成不 flush）、
    cc-flush-after（写者完成 + flush_journal）、cc-mid-write（首轮结束 barrier slack
    后不 join 直接 abort）
  - process_crash_child 三分支调用点 + journal_diag 诊断（rewrite_log_info! 永久化）
  - `persistent_concurrent_crash_recovery_converges`：四相位恢复矩阵（cc-single-put /
    cc-flush-before / cc-flush-after / cc-mid-write），open_persistent + verify_all +
    open_bucket_count==0 + scan 有序断言
- subvol `fe4bf73`：engine.rs +139/-21（确定性修订）
  - JournalWrite 故障注入替代时序假设：cc-single-put / cc-flush-before 在写者前注入 20
    次写盘故障，bch2_journal_flush 写盘前消费注入返回 -5（journal.rs:1009-1015，状态
    推进之前）→ 任何后台 checkpoint 都失败、内存记录保留至 abort 后丢失 → 恢复 0 键确定
  - 移除调试残留（SUBVOL_CC_PUT_ONLY、cc-single-put 测试循环、临时 eprintln）

## 上游锚点（AC-1）

见 ac1-source-anchors.md（replay 语义 / 后台 reclaim / commit.c 锁序 /
写盘失败不推进 seq / T0195-T0199 既有模式）。

## AC 对照

| AC | 验收 | 证据 |
|----|------|------|
| AC-1 | 修改前锚点记录 | 本文件锚点段（replay/flush/commit 语义 + T0195/T0196/T0199 既有模式） |
| AC-2 | 并发崩溃子进程三分支 | cc-flush-before / cc-flush-after / cc-mid-write：4 写者 Barrier(5) 起跑 + TransactionRestart 注入 + 确定性 abort 点 |
| AC-3 | 恢复验证矩阵 | 四相位恢复断言：verify_all 通过、open_bucket_count==0、scan 有序；flush 前场景确定性丢弃（JournalWrite 注入下 0 键实测，journal replay 语义） |
| AC-4 | 注入下崩溃恢复最终一致 | 写者运行期间 TransactionRestart 注入（共享计数被并发消费）不影响崩溃点确定性；cc-mid-write 无注入仅断言最终一致（子集断言，不依赖到达顺序） |
| AC-5 | 生产代码零改动 | 引擎核心零改动（仅测试新增 + journal_diag 日志）；不新增公开 API |
| AC-6 | 全量门禁 | 229 lib + 10 proptest（37.07s ≤1min）+ 5 cli 全绿；fmt --check 通过 |

## 结论

待 verdict 确认。
