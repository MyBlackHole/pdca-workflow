# Skill 入口，共同资源中心

总入口定位和显式绑定；辅助入口只读提出建议；阶段入口操作已有任务；场景入口提供对象与方法。
`skills/catalog.json` 是唯一运行入口名录。安装器只把这九个入口注册到宿主发现目录；
同仓库其他工程 Skill 只作为参考资产，不因位于 `skills/` 而自动获得运行资格。

| Skill | 作用 |
|---|---|
| [pdca](pdca/SKILL.md) | 用户显式选择 PDCA、绑定项目、查询状态或恢复已有任务时使用。定位集中 Git 工作副本与原会话，不自动创建任务或执行四阶段。 |
| [pdca-assist](pdca-assist/SKILL.md) | 仅在用户显式调用 pdca-assist，为当前已绑定项目选择下一步工作建议时使用。普通请求不自动启用。 |
| [pdca-plan](pdca-plan/SKILL.md) | 用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。 |
| [pdca-do](pdca-do/SKILL.md) | 用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。不自动 Check。 |
| [pdca-check](pdca-check/SKILL.md) | 用户明确启动现有 PDCA 任务的 Check 时使用。不修改业务对象或自动返工。 |
| [pdca-act](pdca-act/SKILL.md) | 用户明确批准现有 PDCA 任务的 Act 处置时使用。不启动下一场景。 |
| [pdca-model](pdca-model/SKILL.md) | 用户明确选择本体建模场景，或已有建模任务需要场景方法时使用。不以知识地图冒充模型。 |
| [pdca-implement](pdca-implement/SKILL.md) | 用户明确选择本体投影场景，或已有投影任务需要场景方法时使用。不脱离模型。 |
| [pdca-verify](pdca-verify/SKILL.md) | 用户明确选择本体符合性验证，或该任务需要核验方法时使用。不把链接检查当语义证明。 |

九个运行 Skill 都保持为**薄入口**：

- `pdca`：项目定位、绑定与用户操作分流；绑定/Git 规则以 project-workspace 为准，task 连续性以 entry-recovery 为准；
- `pdca-assist`：只读产生少量有证据的候选，不默认全项目扫描，不创建任何运行对象；
- 四个 phase Skill：只保留阶段触发和阶段特有边界；共同恢复以 entry-recovery、阶段方法以 `flow-*.md` 为准；
- 三个 scene Skill：只保留场景选择、创建前置和路由；场景语义以 [SCENE-01](../ontology/process/work-scenarios.md) 为准；
- Do-only Work Unit 只以 CONTRACT-01 为准。

发现重复规则时回到现有 authority 收敛，不在 Skill/README 维护第二份副本。

Skill 的 `5.0.0-rc.2` 是运行入口包版本，不与 ontology/protocol 的 `4.0.0-rc.x` 比大小；
版本域的唯一说明见 [PDCA：版本域](../ontology/concept/pdca.md#版本域)。
已有 task 绑定优先，读取场景方法不创建场景任务。中央项目/任务登记和资源预约对所有入口相同；
业务项目不自动生成 `.pdca/`。记录写入与 Git 提交分别授权。

正文相对链接从集中工作副本解析，不生成导出副本或规则快照。更新由用户自行使用 Git 完成，
并按宿主能力重启或显式重载。更新不自动改绑活动任务或授权后续阶段。
宿主发现与交互以[现场验收](../tests/host-acceptance.md)为准。

## 分解边界

正式 task 与 Do-only Work Unit 必须分开：

- 正式节点只按 [NODE-01](../ontology/concept/work-node-contract.md) /
  [DECOMP-01](../ontology/concept/task-decomposition.md) 从固定 ontology/work relation 形成，
  并由 [CONTEXT-01](../ontology/process/select-task-subgraph.md) 建立独立上下文边界；
- Work Unit 只按 [CONTRACT-01](../ontology/concept/pdca-execution-contract.md) 服务于当前已批准 Do，
  不创建 node/task/attempt，也不获得新的 ontology responsibility；
- LOC、工时、token、并行度或 Agent 置信度都不能单独产生正式任务。

具体语义只维护在上述 authority；本索引不再复制它们的字段、调度或恢复规则。
