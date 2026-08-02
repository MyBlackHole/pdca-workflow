# T0174 btree 分裂压力属性测试

## 问题

T0168 矩阵 A1 显示 btree split 实现与 bcachefs interior.c 对齐「部分」：
多级分裂依赖 restart 重试语义（interior.rs:447），未对齐 interior.c 完整
异步 update_start 语义。但更基础的问题是：**分裂路径在所有属性测试中
零触发**——节点容量 ~32k u64s（约 5000+ 键，interior.rs:9 + io.rs:256），
而属性测试 key 空间仅 216 组合（btree_proptest.rs:32）、ops ≤ 120，
最多写入 120 个键，远不足以填满单节点，**btree 恒深 1**。

多级分裂（leaf split → 内部节点更新 → root 分裂）是 btree 操作正确性
（AGENTS.md 首要交付）的核心路径，当前无属性级验证。

## 目标

新增属性测试：扩大 key 空间保证写满节点并触发多次分裂（深度 ≥ 2，内部
节点存在，restart 重试路径被踩到）+ 崩溃恢复，验证分裂后不丢键、scan
全量一致、root topology 正确。

## 用户故事

作为存储引擎开发者，我希望在随机操作流中强制触发 leaf/interior 分裂并
崩溃恢复，以便验证：多级分裂重试语义（restart）在任何崩溃窗口下都不丢
键、不重复、与内存模型一致（bcachefs 语义：分裂是事务内的拓扑变更，
split_leaf 失败路径 restart 重试，对齐 interior.c/btree_split.c）。

## 方案

btree_proptest.rs 新增第 6 个 proptest `split_stress_preserves_model`：

- **阶段 1（确定性分裂）**：预写 2000 个唯一键（inode=1、offset 1..=2000、
  snapshot=0、值 1 u64s）。节点容量实测上界：BCH_SB_BTREE_NODE_SIZE=8 扇区
  =4KB（io.rs:737 flags[0]=8<<12），max_u64s ≈ (4096-头部)/8 ≈ 470，
  最小键 4 u64s → 单节点最多 ~118 键 → 2000 键必然分裂出 17+ 叶子、
  root 分裂、深度 ≥ 2（AC-1 由容量必然性保证，无需统计概率）。
- **阶段 2（随机压力 + 崩溃恢复）**：split 键空间
  `(1u64..=4, 1u64..=2048, 0u32..=2)`=24576 唯一键，
  `ops in vec(split_op_group_strategy(), 1000..=2000)`（每组 ~3.5 op）、
  `crash_every in 300usize..=800`（每 case 恢复 ≤7 次）
- 每步：apply_group + apply_model（同既有框架）
- crash 步骤：`sync` → drop → `open_persistent` → `assert_model`
- 收尾：最终 sync + drop + open_persistent + assert_model
- 断言复用 `assert_model`（scan 全量 + 键序 + `verify` root topology，
  engine.rs:534）——兼容多级树

## 实现决策

| 决策 | 选择 | 依据 |
|------|------|------|
| 分裂触发 | 阶段 1 确定性预写 2000 键 | 节点 4KB/最多 ~118 键，容量必然性保证分裂，无统计风险 |
| 随机段键空间 | 4×2048×3=24576 组合 | 足够大，随机 op 不触发二次容量瓶颈 |
| 随机段规模 | ops 1000..=2000 组 | 压力 + 时间预算（~2-5s/case，约束 9） |
| crash 频率 | crash_every 300..=800 | 恢复 ≤7 次/case，时间可控 |
| 断言 | 复用 assert_model（scan+verify） | engine.rs:534 verify 检查 root topology，兼容多级树 |
| 约束 12/13 | 无自有逻辑；仅新测试策略函数（测试设施，非运行时逻辑） | 对齐 T0168 AC-4 测试设施豁免 |

## 验收标准

- [ ] AC-1: 测试触发真实分裂（深度 ≥ 2，验证内部节点存在）
- [ ] AC-2: 每次 crash 恢复后 `assert_model` 通过（不丢键、不重复）
- [ ] AC-3: 最终恢复后 `assert_model` 通过
- [ ] AC-4: 与既有 5 个属性测试共存，全量回归绿（lib 173 + 集成全部）+ fmt 干净
- [ ] AC-5: 连续 8 轮 proptest 稳定通过，单轮 ≤ 60s（约束 9）

## 范围外

- interior split 异步 update_start 语义对齐（T0168 P1，本任务只验证现有
  重试语义正确性，为后续对齐提供基线）
- verify 递归全树增强（T0168 P2 D4）
- seq 环回/黑名单（D2）、trigger 链（D3）、逐 key 校验（D5）
- 任何引擎实现修改（纯测试任务）

## 备注

- 提交：feature-commit-format（【F-T0174】engine: 新增 btree 分裂压力属性测试…，
  0.1.0 -> 0.1.0）
- 单一格式版本，无兼容性影响
