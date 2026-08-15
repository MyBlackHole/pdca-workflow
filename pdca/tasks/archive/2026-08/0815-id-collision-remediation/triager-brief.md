# T0274 Triage Brief

## 分类

- **category**: bug（identity 数据完整性缺陷，历史遗留）
- **scenario_type**: development

## 事实核验

- 已验证：doctor `identity.duplicate_task_ids` 报告 23 组，每组同一 task_id 出现在 2-3 个目录，且各目录为**真实独立任务**（各自有 task.json/record/归档状态）。
- 已验证：根因均为 `legacy`（task_identity.py 引入前的历史重复分配），非外部项目、非真缺陷。
- 已验证：rpc-epoll 链（T0213→T0214→T0215-T0222）parent 引用完整，T0214 被引用 10 次；CDM/报表链与 backup/round 链各自占用相同 ID。
- 已验证：部分组涉及活跃任务（T0216/T0218/T0219/T0220/T0221/T0222/T0228/T0229/T0248/T0250/T0252 处于 plan/do/check）。

## 查重

- T0261（统一 task/record identity）实现身份合约但未清理存量；T0262/T0263 观察 identity 上线效果；T0272 诊断出撞车清单但明确"候选不执行"。本任务是 T0272 修复候选清单中 highest 项的执行。

## 方案（用户已确认）

1. **全链路重分配 ID**：为撞车组中"非主流"一方分配新 ID（T0274+ 后缀或 Txxxxc 后缀，参照 T0210b 先例），同步 task.json / records 目录 / parent-children 引用链 / 归档目录名。
2. **跳过活跃任务**：涉及 active 任务（phase=plan/do/check）的撞车组不处理，记录到处置报告的"待办"段，等其归档后执行。
3. **产出完整处置报告**：逐组判定谁保留谁重分配、引用链影响、records 对应、执行顺序与验证方式，写入 records/ 作为执行依据。

## 验收标准

- 运行检查得到 23 组中可处置组的完整处置映射（保留方/重分配方/新 ID/受影响引用）。
- 处置报告列明跳过组（活跃任务）及原因。
- 诊断脚本对已处置组验证无重复。

## 范围外

- 不处理活跃任务的撞车组（待归档后另立任务）。
- 不修改历史 task.json 以外的不可变记录内容（仅目录/ID 映射）。

## 信息缺口

- 各组"主流/非主流"判定需要逐组核对 parent 链与 title 归属。

## 推荐下一步

- Grill 确认主流方判定规则 → PRD → 执行处置 → 验证。
