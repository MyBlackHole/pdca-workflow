# 八个入口，共同资源中心

总入口定位；阶段入口操作已有任务；场景入口提供对象与方法。不是七阶段流水线，也不是每次调用新建Agent。安装器把下列正文及实际集中根导出到宿主发现目录，不只放一句跳转。

| Skill | 作用 |
|---|---|
| [pdca](pdca/SKILL.md) | 用户显式选择 PDCA，查询状态或恢复已有任务时使用。定位集中资源根与原会话，只分流，不自动创建任务或执行四阶段。 |
| [pdca-plan](pdca-plan/SKILL.md) | 用户明确启动或继续现有 PDCA 任务的 Plan 阶段时使用。与用户确认问题和目标，在原 Agent 内制定计划并等待 Do 授权。 |
| [pdca-do](pdca-do/SKILL.md) | 用户明确启动或继续现有 PDCA 任务的 Do 阶段时使用。核对批准计划、集中资源和原会话，只实施当前 run，不自动 Check。 |
| [pdca-check](pdca-check/SKILL.md) | 用户明确启动现有 PDCA 任务的 Check 时使用。核验固定产物、标准和证据，在原会话完成，不修改业务对象或自动返工。 |
| [pdca-act](pdca-act/SKILL.md) | 用户明确批准现有 PDCA 任务的 Act 处置时使用。按批准范围交付、归档或发布，记录资源结清后停止，不启动下一场景。 |
| [pdca-ontology-modeling](pdca-ontology-modeling/SKILL.md) | 用户明确选择本体建模场景，或已有建模任务需要场景方法时使用。定义领域模型与工作实例交付；不以知识地图冒充模型，不自动开始 Plan。 |
| [pdca-ontology-projection](pdca-ontology-projection/SKILL.md) | 用户明确选择本体投影场景，或已有投影任务需要场景方法时使用。从固定模型产生目标产物和映射，不脱离模型或自动启动符合性验证。 |
| [pdca-ontology-conformance-verification](pdca-ontology-conformance-verification/SKILL.md) | 用户明确选择本体符合性验证，或该任务需要核验方法时使用。分别检查需求到模型、模型到投影、产物到行为，不把链接检查当语义证明。 |

四阶段每次匹配用户操作后启动，完成后停止；一个任务使用多个Skill但保持原Agent。已有task绑定/快照优先，读取场景方法不创建场景任务。中央项目/任务登记和资源预约对所有入口相同；业务项目不自动生成.pdca。

`catalog.json` 是安装用名录，不是授权表。源正文内的相对链接由安装器解析到固定规则快照的绝对链接。安装目录中的正文是导出副本，勿手改；修改维护源后更新发布并重新安装。安装更新不切换活动任务版本。
