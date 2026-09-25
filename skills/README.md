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

四阶段每次匹配用户操作后启动，完成后停止；一个任务使用多个 Skill 但保持原 Agent。
已有 task 绑定优先，读取场景方法不创建场景任务。中央项目/任务登记和资源预约对所有入口相同；
业务项目不自动生成 `.pdca/`。记录写入与 Git 提交分别授权。

正文相对链接从集中工作副本解析，不生成导出副本或规则快照。更新由用户自行使用 Git 完成，
并按宿主能力重启或显式重载。更新不自动改绑活动任务或授权后续阶段。
宿主发现与交互以[现场验收](../tests/host-acceptance.md)为准。

## 分解：正式工作节点与 Do-only Work Unit

两种分解必须分开，不能把执行切片自动升级为新的 PDCA 任务。

### 正式工作节点

正式工作节点必须先来自固定 ontology/work instance 中的具名 object/node 及语义关系，
再满足**独立职责、固定输入/输出、可独立拒收成果和验证边界**。
[DECOMP-01](../ontology/concept/task-decomposition.md) 只从这种 ontology-backed candidate 生成 seed。
用户明确批准后，宿主创建 fresh Agent；[CONTEXT-01](../ontology/process/select-task-subgraph.md)
按该 node 选择 minimum sufficient ontology subgraph，而不是复制父/兄弟完整上下文。
每个正式节点执行完整 Plan→Do→Check→Act，父 Agent 不监控其生命周期。

### Do-only Work Unit

一个已批准正式 Task 的 Do 内部需要局部执行、隔离分析或缩小执行范围时，使用 Do-only Work Unit。
Work Unit 不是任务、不是第五阶段，不拥有独立 Plan/Check/Act，也不触发新的阶段授权。
它只执行父 Do 已固定范围的一部分，并使用
[CONTRACT-01](../ontology/concept/pdca-execution-contract.md)定义的
`C=(I,O,S,R,T,Φ,Ψ)` 边界。

- 可在原 Agent 内执行，也可委派给隔离上下文的执行者或外部工具；不绑定具体宿主 API。
- 它的输入是正式 Task 子图的进一步局部切片，不建立新的 ontology/task 上下文边界。
- 父 Do 不轮询、不监工；只消费原生完成事件、固定结果或用户主动返回的结果。
- Work Unit 若需要扩大目标、AC、写域、资源或不可逆副作用，立即停止并回到用户授权边界。
- 数据依赖可定义阻塞边；“ready”只表示当前 Do 内可执行，不授权创建新的正式任务。

不使用 LOC、预计工时、token、并行度或 Agent 置信度作为正式任务拆分依据。详细设计见
[Do 工作单元与正式节点拆分](../docs/superpowers/specs/2026-09-15-subtask-splitting-design.md)。
