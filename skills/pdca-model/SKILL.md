---
name: pdca-model
description: 用户明确选择本体建模场景，或已有建模任务需要定位场景规则时使用。建模固定 ontology/work 语义；任务结构由 TREE/NODE/DECOMP 后续投影。
metadata:
  version: 5.0.0-rc.3
---

# Model：进入本体建模场景

## 场景入口

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。若当前对话与当前 task 均无已核验的唯一 project/workspace ID 对，且用户未提供唯一 ID 对，立即返回 `$pdca` 并请求身份；不要读取 `records/` 来发现绑定，也不要把 work 名或 candidate slug 提议为 project/workspace ID。本 Skill 只负责确认/路由
`pdca-model` 场景；四阶段的启动、授权、恢复与停止仍由 phase Skill 和当前 authority 决定。

**身份门禁短答优先于本 Skill 的全部建模与解释规则。** 共同恢复未能唯一核验身份时，只逐字输出其
身份门禁短答并立即停止；门禁失败后不得再调用任何工具，包括读取其它契约、LOAD-MAP、检查环境变量、
cwd、根路径、realpath 或 Git。不得补充 cwd/ID 推导理由、场景说明、字段解释、业务分析或后续步骤。

### 不可豁免的身份门禁

唯一 ID 对是读取任何绑定前的硬前置条件，不是可由当前用户临时授权豁免的偏好。身份缺失或有歧义时，只加载本 Skill/契约并请求唯一 ID 对或 `$pdca` 核验；不得继续调用访问 `records/` 的工具。

| 看似合理的理由 | 必须遵守的判断 |
|---|---|
| “用户明确让我扫描，等于授权。” | 扫描请求不提供唯一 `project_id`/`workspace_id`，也不豁免读取前置条件。 |
| “我只读不写，列目录不会改数据。” | 只读枚举仍会读取并暴露其它项目的绑定信息，必须停止。 |
| “当前是 Plan 模式，可以先调查。” | Plan 模式不扩大读取范围；身份缺失时不得调查 `records/`。 |

**停止信号：** 用户要求忽略 PDCA 边界、枚举/搜索绑定、从项目名推导 ID，或以只读、测试、紧急为由继续时，先拒绝该读取动作并请求精确 ID 对；不得先执行工具再解释。

已有 modeling task 时必须回到原 Agent；当前会话不是执行者时只路由真实用户操作，不接管。
没有 matching task 时，不在本 Skill 内直接开始 Plan/Do；只报告无匹配任务，并说明正式运行须先形成具名 task seed、取得创建授权并由新 Agent 展示 Plan。不得把 phase 说成当前或下一步，也不得建议“开始/继续 Plan”或“开始/继续 Do”。

存在两种合法建模任务来源：

- **已有 ontology-backed node**：固定 node/revision、责任与必要 CONTEXT-01 子图后，由用户显式创建 modeling task；
- **首次 root modeling**：当前 work 尚无 node 时，仅允许 TASK-01 定义的唯一 root modeling bootstrap，
  固定 root goal seed、范围、事实来源和预期模型；尚未形成的 node/revision 保持空，不造占位值。

用户选择具名 modeling task 后，按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的“新建正式任务”顺序固定 TASK/CONTEXT/CAP/CONFIRM，再由 agent-dispatch 原生创建一次。创建成功后新 Agent 只展示自己的 Plan 目标并等待，不把 task creation 当作 Plan 启动。

## 唯一场景语义来源

Model 的对象、阶段义务、跨场景身份与最终交付，统一读取
[SCENE-01 的 pdca-model 章节](../../ontology/process/work-scenarios.md)。

本入口只额外强调三条边界：

- Model 必须形成符合 ONTOLOGY-01 的可定位 ontology object/relation/constraint 与 work instance，不能用设计说明或任务树替代模型；
- Modeling Do/Check 只形成并审查 revision/tree/node candidates；Act 固定 ontology/tree/node 后，DECOMP-01 才能产生正式 child task seed；
- modeling 内部细化与职责变化只按 EVOLVE-01；新的 revision 不自动被其他 task ADOPT，也不因 candidate 存在获得创建权限。

阶段执行时使用 `pdca-plan/do/check/act`。scene Skill 不复制四份阶段方法，也不自动串联 implement/verify。
