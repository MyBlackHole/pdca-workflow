# PDCA 工作流 — 强制执行协议

PDCA_HOME 环境变量指向管理中心（pdca-workflow 仓库）。
所有 flows/ 和 ontology/domain/ 引用以 `$PDCA_HOME` 为前缀。

## 强制规则

所有任务必须按 **Plan → Do → Check → Act → Archive** 五阶段推进，严格遵循各阶段流程文件：

| 阶段 | 流程文件 | 核心产出 |
|------|---------|---------|
| Plan | `$PDCA_HOME/flows/flow-plan/SKILL.md` | task.json + prd.md |
| Do | `$PDCA_HOME/flows/flow-do/SKILL.md` | 实现产物 + evidence |
| Check | `$PDCA_HOME/flows/flow-check/SKILL.md` | conclusion.md + verdict |
| Act | `$PDCA_HOME/flows/flow-act/SKILL.md` | disposition + 归档 |

1. **必须先读取对应阶段的流程文件**，按步骤执行，不得跳过步骤。
2. Plan 阶段必须先创建 task.json（写入 `$PDCA_HOME/pdca/tasks/`），写 prd.md，经用户确认后才进入 Do。
3. Do 阶段按 `meta.scenario_type` 选择路径，完成后登记 evidence。
4. Check 阶段写 conclusion.md 并获取用户 verdict。
5. Act 阶段完成知识处置和 disposition 后归档。
6. 不得通过直接修改 task.json 跳过门禁。所有阶段转换必须经过 advance-phase 校验。

任务写入 `$PDCA_HOME/pdca/tasks/`，记录写入 `$PDCA_HOME/records/`。