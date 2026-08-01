# T0174 Triage Brief

## 分类
- category: enhancement / scenario_type: development
- 来源：用户「PDCA 下一步推荐」+ T0168 拆解表 P1（interior split 语义对齐）的前置验证

## 查重结果
- active/archive 任务均无分裂相关属性测试（T0169 修复 commit 空间检查，
  其回归测试为单 leaf 多 update 场景，不覆盖多级分裂）；knowledge 无相关条目
- 结论：不重复

## Claim 验证
- 节点容量：btree_buf_max_u64s ≈ (256KB - 头部)/8 ≈ 32k u64s（interior.rs:9，
  容量由 superblock BCH_SB_BTREE_NODE_SIZE 固定，io.rs:256）
- 属性测试 key 空间：key_strategy (1..=3, 1..=24, 0..=2) = 216 组合；
  ops ≤ MAX_OPS=120（btree_proptest.rs:24/32）→ 最多写入 120 个键，
  远不足以填满单节点 → **btree 分裂路径（bch2_btree_split_leaf，
  interior.rs:380）在所有属性测试中零触发，btree 恒深 1**
- 引擎依赖多级分裂重试语义（interior.rs:447 注释：restart 重试），
  该路径无属性级验证，与 T0173 的 reclaim 冷路径问题同构

## 信息缺口
- 扩大 key 空间后是否必然触发分裂（需写满 ≥1 节点 + 继续写）
- 分裂后 verify/恢复断言是否与既有 assert_model 兼容（verify 支持多级树？）

## 推荐下一步
1. 首选：T0174 分裂压力属性测试（本次 triage 已建骨架）
2. 备选：interior split 语义对齐（P1，大工程，建议 T0174 之后）
3. 备选：seq 环回评估（D2/P1，实际影响极小）
4. 备选：CI/回归脚本集成

## 日期
2026-08-01
