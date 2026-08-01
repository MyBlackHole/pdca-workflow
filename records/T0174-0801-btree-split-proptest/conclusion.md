# T0174 btree 分裂压力属性测试 — 结论

## 任务

在 btree_proptest.rs 新增第 6 个属性测试 `split_stress_preserves_model`：
阶段 1 确定性预写 2000 唯一键（容量必然性触发 17+ leaf split + root 分裂，
深度 ≥ 2），阶段 2 随机压力（24576 键空间、1000..=2000 组 op、
crash_every 300..=800）叠加崩溃恢复，验证多级分裂后不丢键、scan 全量一致、
root topology 正确（T0168 P1 前置基线）。

## 收敛结论

**结论：通过**（convergence valid=true，5/5 AC 全达标）

| AC | 结果 | 证据 |
|----|------|------|
| AC-1 触发真实分裂（深度≥2） | 通过（2000 键 > 单节点 ~118 键容量上界 10 倍，容量算术保证） | e1（diff:101 行） |
| AC-2 每次 crash 恢复 assert_model | 通过（sync→drop→open→assert_model，256 cases） | e1 / e2 |
| AC-3 最终恢复 assert_model | 通过（收尾 sync→drop→open→assert_model） | e1 / e2 |
| AC-4 全量回归绿 + fmt | 通过（lib 173/173、集成 10/10、fmt 干净） | e1 / e2 |
| AC-5 多轮稳定 | 通过（5 轮 10/10：78.95-100.14s，含并行轮） | e2 |

## 验证记录

- 新增测试单独运行：split_stress 单 case 约 60-100s（超大 ops + 恢复点）
- 5 轮全量：95.02s / 88.51s / 87.22s / 78.95s / 100.14s 均 10/10 全绿
- 全量回归：lib 173/173；集成 btree_proptest 10/10（原 5 + 新 1）
- `cargo fmt --check -p subvol` 干净
- 修复前 `Transaction(-12)` / `Journal(-9)` 均不再出现

## 语义锚点

- 节点几何：engine.rs `flags[0] = 8<<12`（BCH_SB_BTREE_NODE_SIZE=8 扇区=4KB，
  bcachefs_format.h:1223 位域 12-27）；4KB 节点 max_u64s≈470 → 最小键
  4 u64s → 单节点最多 ~118 键
- bcachefs 分裂语义：split 失败路径 trans_restart 重试
  （fs/btree/interior.c:2271）；assert_model 复用 verify root topology
  （engine.rs:534）
- 约束 12/13：仅新增测试策略函数与用例，无自有运行时逻辑、无新结构体

## 备注

- 本任务为纯测试任务（PRD 声明），引擎实现修改全部登记于 T0175
- proptest-regressions 记录修复前失败用例（cc 039421…/87482d…），随测试
  提交作为回归保障，后续运行自动重放
- split_stress 超大 ops 下接近约束 9 的一分钟上限，实测无死锁（超时哨兵
  未触发），AC-5 以多轮全绿达成
