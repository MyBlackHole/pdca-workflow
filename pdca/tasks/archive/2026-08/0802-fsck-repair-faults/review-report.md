# T0200 代码审查报告

审查对象：subvol `f404fec`（engine.rs +173/-8）

## 约束合规

| 约束 | 状态 | 说明 |
|------|------|------|
| 1 对照本地代码 | ✓ | 锚点：commit.c:1390、iter.h:1115-1127、alloc/check.c:366-371、fsck.rs:457-460 |
| 3 逻辑一致 | ✓ | -4 走既有重试循环（lockrestart_do 语义）、-12 硬失败走既有错误传播，无新控制流 |
| 6 不简化 | ✓ | 重试、错误传播、回滚路径原样保留 |
| 8 无新函数 | ✓ | 仅既有函数改造 + 测试；fsck_image_with_fault 为测试入口（对齐 recover_with_fault 先例） |
| 12 无自有逻辑 | ✓ | 注入位点/语义均在上游有对应（trans_maybe_inject_restart、fs.exit 失败传播） |
| 13 无自有结构体 | ✓ | FsckFaultPoint 对齐 RecoveryFaultPoint 既有形态（T0196 已确立的模式） |

## 变更点审查

1. **bit_mod_sync -4 重试分支**：`ret == -4 || (ret == -12 && realloc != 0)`，
   与 reclaim_bucket（1090）、allocate（886）逐字一致；修复了 T0198
   缺口（真实 -4 restart 下修复事务误中止）。✅
2. **注入位点**：事务提交前（bch2_btree_bit_mod 成功且 fault 匹配时），
   对齐 trans_maybe_inject_restart 的提交前位置。fault 一次性消费
   （`*fault = None`），后续事务不受影响。✅
3. **DuringRepairOom**：注入 -12 不置 realloc_bytes_required（默认 0），
   不满足重试条件 → bch2_trans_put → Err(Transaction(-12))。✅
4. **AfterRepairBeforeFlush**：修复提交后、flush 前返回 Journal(-5)，
   与 flush_journal 的 Journal 错误变体一致。✅
5. **公开 API**：fsck_image 签名/行为不变（fault=None 与旧实现等价）。✅

## 测试审查

- restart 注入：验证 -4 重试收敛（消费一次后成功）✅
- OOM 注入：Err(Transaction(-12)) + 重跑恢复 + verify_all ✅
- flush 失败：Err(Journal(-5)) + 重跑恢复（未落盘修复被 journal 回放
  丢弃语义实测确认）✅
- 矩阵：OOM/Flush 均 Err，restart 排除（重试非失败）✅

## 结论

通过。无阻塞项。
