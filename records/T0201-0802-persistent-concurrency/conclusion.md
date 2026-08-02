# T0201 结论

## 任务结果

T0201 已完成，待确认（verdict 待定）：持久化并发交错（并发写者 ×
确定性崩溃点 × 恢复验证）组合验证全部通过。

## 交付物

- subvol `c571798`：engine.rs +128（T0201 主体）
  - `concurrent_crash_child`：4 写者线程（btree put + allocate/reclaim
    双回收）× Barrier(5)（4 写者+主线程，T0199 规则）+ 一次性
    TransactionRestart 注入；三分支崩溃点（flush-before / flush-after /
    mid-write）
  - `persistent_concurrent_crash_recovery_converges`：四相位恢复矩阵
  - journal_diag 崩溃点诊断日志（rewrite_log_info! 永久化）
- subvol `fe4bf73`：engine.rs +139/-21（确定性修订）
  - JournalWrite 故障注入（20 次）替代时序假设：flush 前场景恢复
    0 键确定（写盘失败在 seq 推进前返回 -5，journal.rs:1009-1015）
  - 移除调试残留（SUBVOL_CC_PUT_ONLY、临时 eprintln）

## 关键结论

1. **未落盘丢弃语义实测**：cc-single-put / cc-flush-before 注入
   JournalWrite 故障后，后台 reclaim 任何 flush 尝试都失败，12 个
   已提交事务全部留在内存，abort 后恢复 0 键——journal replay 只
   回放已落盘事务的语义被确定性验证（AC-3）。
2. **后台 reclaim 竞态是引擎正常行为**：journal 初始即 med=true
   （4 桶几何边界），每次 commit 都 schedule_reclaim_if_needed，
   worker 25ms 周期内可能落盘——cc-mid-write 不注入时存活集不确定
   （与 bcachefs background journal reclaim 一致），断言只依赖最终
   一致（子集断言，T0199 原则）。
3. **stop_background_reclaim 方案不可行**：request_reclaim_inner 在
   stopping 时返回 Transaction(-1)（engine.rs:1767，Drop 语义：
   stopping=只读，对齐 bcachefs ro 后拒新事务），停 worker 后 put
   必然失败——确定性方案只能走故障注入路径（T0196 机制）。
4. **崩溃点诊断永久化**：abort 前 journal 状态（seq_ondisk/space/
   closed 等）经 rewrite_log_info! 输出，注入场景 seq_ondisk=0 可
   人工核对（对齐"用日志 API 替代临时 eprintln"指示）。

## 数值

- 全量 244 测试全绿（229 lib + 10 proptest + 5 fsck_cli）
- proptest 单项 37.07s ≤ 1min（AC-6 门禁）
- 并发崩溃测试单项 1.50s，全量 lib 10.30s
- cargo fmt --check 通过

## 遗留

- 无。范围外项（模型 op 域扩展、多镜像并发 fsck、真实磁盘故障
  模拟）留待后续任务。
