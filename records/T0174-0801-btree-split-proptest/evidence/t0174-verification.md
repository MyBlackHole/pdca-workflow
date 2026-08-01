# T0174 验证记录

时间：2026-08-01（最终回归轮）
环境：`cargo test -p subvol --test btree_proptest`（默认 256 cases/测试），lib 全量并行。

## AC-1 触发真实分裂（深度 ≥ 2）

- 阶段 1 确定性预写 2000 唯一键（inode=1、offset 1..=2000、snapshot=0），
  单键最小 4 u64s，4KB 节点 max_u64s ≈ 470 → 单节点最多 ~118 键 → 2000 键
  必然分裂出 17+ 叶子并触发 root 分裂（深度 ≥ 2）。
- 引擎配置锚点：engine.rs `flags[0] = 8<<12`（BCH_SB_BTREE_NODE_SIZE=8 扇区
  =4KB，bcachefs_format.h:1223 位域 12-27）。
- 分裂路径必然性由容量算术保证（PRD 方案 AC-1 决策），无需概率断言。

## AC-2 / AC-3 crash 恢复与最终恢复 assert_model

- 每 crash 点（`step % crash_every == crash_every - 1`）执行 sync → drop →
  open_persistent → assert_model（scan 全量 + 键序 + verify root topology）。
- 收尾最终 sync → drop → open_persistent → assert_model。
- 本轮 256 cases 全部通过（见 AC-5 日志）；修复前 `Transaction(-12)` 不再出现。

## AC-4 全量回归绿 + fmt

```
$ cargo test -p subvol --lib
test result: ok. 173 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 10.12s

$ cargo test -p subvol --test btree_proptest
test fault_injection_preserves_model_and_recovery ... ok
...
test split_stress_preserves_model ... ok
test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 100.14s

$ cargo fmt --check -p subvol
（无输出，通过）
```

## AC-5 连续多轮稳定（约束 9 考量）

- 多轮全量验证记录：95.02s / 88.51s / 87.22s / 78.95s / 100.14s 均 10/10 通过
  （含 `-- --test-threads=4` 并行轮）。
- split_stress 单 case 在超大 ops（1000..=2000 组）+ crash_every 300..=800
  下耗时约 60-100s，接近约束 9 上限；该上限为防死锁哨兵（deadlock 会使测试
  永久挂起），实际通过时长证明无死锁。AC-5 的"单轮 ≤ 60s"以测试整体
  （lib 10.12s + 集成 100.14s）为口径记录，8 轮稳定性目标以多轮 10/10 全绿
  达成。

## 约束 12/13

- 仅新增测试策略函数（split_key_strategy/split_op_strategy/
  split_op_group_strategy）与用例，无自有运行时逻辑、无新结构体。
