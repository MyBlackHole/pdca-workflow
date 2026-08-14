# T0261 Research Execution Plan

## 冻结假设与预测

| 假设 | 验证前预测 | 独立 oracle | 反证条件 |
|---|---|---|---|
| H1：普通 Plan 任务缺少统一原子 ID 分配入口，允许并发会话选择相同 next ID | 仓库只存在晋级专用的 `_next_task_id` + promotion lock；普通任务由说明/代理直接建文件，两个并发创建者可读取相同最大 ID | 源码/流程入口枚举；隔离临时仓库并发复现；历史创建时间 | 找到所有普通创建都必须经过的原子分配器，或真实并发路径不能产生重复 ID |
| H2：Improvement Candidate 晋级路径不是当前碰撞来源 | promotion lock 覆盖查重、next ID 和目录创建，独占写入拒绝冲突；并发 promotion 负对照保持唯一 | `scripts/flow_issues.py`、现有并发测试及隔离复现 | promotion 并发可生成两个不同 slug、相同 task ID，或锁未覆盖关键区间 |
| H3：5 个 EVENT_PATH_MISMATCH 来自 record identity 在事件写入后发生目录迁移/归并 | 事件 ID 与 payload record_id `T0252` 一致，但文件最终位于完整 record 目录；历史或操作记录能找到移动/归并边界 | event ID 重算、git/history、task meta.record 与目录时间线 | 事件从创建时就由 report CLI 直接写入不匹配目录，或发现其他写入器绕过 path 合约 |
| H4：task ID 冲突是风险放大器，但不等同于 mismatch 的充分原因 | 存在冲突而无 mismatch 的负对照；只有 record 目录/payload 不一致才令聚合失败 | 全仓库 collision×mismatch 交叉表 | 所有冲突都确定性导致 mismatch，且无独立 record 生命周期因素 |

若 H1–H4 均无法获得独立支持，最终根因标记 `inconclusive`，不产出代码修复候选。

## 工作包

1. 枚举普通任务、to-tickets、promotion、外部初始化及历史迁移的身份创建/移动入口。
2. 对 23 个 collision ID 和 5 个 mismatch event 建立来源、时间、路径、task/record 关系矩阵。
3. 在临时仓库运行正常路径负对照和并发/迁移复现，不修改正式任务、records 或 backlog。
4. 复核冻结预测，给出 supported / rejected / inconclusive，保留反证。
5. 比较两类方案，并评估最小兼容方案：全局原子 task ID；不可变 record identity 为主；必要时组合方案。
6. 仅在根因获独立支持时编写 Improvement Candidate 草案、paired-test 设计与 development seam 草案。

## 拆解判断

保持单一 research 任务。入口枚举、历史分类、复现和方案比较共享同一身份矩阵；拆成子 PDCA 会在根因尚未确认时提前固化方案，并增加口径漂移。
