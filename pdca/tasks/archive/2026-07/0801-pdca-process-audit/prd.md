# PDCA 流程修复 + 自动问题记录能力增强 — 规格文档

## 问题陈述

### 背景
T0150（Parquet 格式深度技术调研）执行过程中暴露了以下 PDCA 流程执行问题：

1. **子任务管理失效**：P4 拆解的 T0151-T0157 共 7 个子任务在创建后从未走独立 PDCA 周期，全部停滞在 `plan/Pending/active=false` 状态
2. **Do 阶段未检查 agent.spawn 能力**：直接使用 task 工具而未经流程规定的能力检查
3. **Check 阶段 Ch2 Grill 被跳过**：未加载 grilling skill 追问结论可靠性
4. **时间戳不一致**：created/plan 时间与 do 时间违反非递减约束
5. **AC 编号格式问题**：register-evidence 与 validate-convergence 使用的 AC 格式不统一
6. **证据注册后 manifest 条目丢失**：tuning 证据首次注册后 manifest 中无对应条目

### 根因
PDCA 流程缺少执行过程中的**自动问题检测与记录机制**，导致流程偏差只能靠事后人工复盘发现，无法即时捕获和积累。

### 目标
1. 修复 T0151-T0157 子任务的遗留状态
2. 为 PDCA 流程增加自动问题记录能力，使每次流程执行中的偏差能被自动检测并记录

## 范围

### 范围一：修复子任务遗留状态
- 清理 T0151-T0157 的子任务：将他们归档并注明原因
- 确认父任务 T0150 已归档无误

### 范围二：自动问题记录机制
- **实现方案**：在 `advance-phase.py` 脚本的每个 phase transition 逻辑中嵌入审计检查点
- 转换时自动检测当前阶段的流程偏差，结果记录到 `$PDCA_HOME/records/<record-id>/flow-audit.json`
- 覆盖的检测点：
  - **Plan→Do**：子任务是否全部创建？是否有子任务 active=false？final_confirmation 是否存在？
  - **Do→Check**：evidence 是否已注册？AC 覆盖是否完整？evidence digest 与 manifest 是否一致？
  - **Check→Act**：verdict 是否已记录？conclusion.md 是否存在？
  - **Act→Archive**：disposition 是否已记录？
- 审计不阻止转换（只记录不 blocking），区别于门禁

## 验收标准

- [ ] T0151-T0157 已归档，归档原因明确
- [ ] 流程审计记录机制已实现（脚本或 skill）
- [ ] 审计记录至少覆盖 Plan→Do、Do→Check、Check→Act、Act→Archive 四个转换点
- [ ] 审计记录输出到 `$PDCA_HOME/records/<record-id>/flow-audit.json`
- [ ] 审计结果包含明确的 pass/fail 和问题描述
- [ ] 当前任务（T0158）执行中能捕获到流程问题

## 范围外
- 不修改 PDCA 的 phase transition 门禁逻辑
- 不改变现有的 advance-phase 脚本核心逻辑
- 不重写现有 flow-*.md 文件（只增加审计步骤而非替换）
