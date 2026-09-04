# PDCA Workflow 项目代理入口

本仓库是 PDCA 管理中心。开始任何任务前，先读取本文件，再按 `$PDCA_HOME` 读取权威流程和技能文件。

- `PDCA_HOME` 必须指向本仓库根目录；未设置时使用当前仓库路径作为 PDCA_HOME，并提示用户配置环境变量
- 活跃任务：`$PDCA_HOME/pdca/tasks/`
- 归档任务：`$PDCA_HOME/pdca/tasks/archive/`
- 不可变记录：`$PDCA_HOME/records/`
- 可复用知识：`$PDCA_HOME/ontology/domain/`
- 工作日志：`$PDCA_HOME/pdca/journal/`

## 必须遵守的 PDCA 门禁

任务严格按 `plan → do → check → act → archive` 推进：

1. Plan 阶段完成 triage、逐轮 Grill、方向确认、PRD 和任务拆解。
2. 只有当前任务 `clarifications.jsonl` 存在用户确认的 `source: "final_confirmation"`，才能进入 Do。
3. Do 阶段按 `meta.scenario_type` 执行，并通过 `register-evidence` 登记证据后才能进入 Check。
4. Check 阶段必须对照 PRD、证据和收敛条件写入 `records/<record-id>/conclusion.md`，并取得结论确认后才能进入 Act。
5. Act 阶段必须完成知识处置、journal 和 `meta.disposition`，通过门禁后才能归档。

不得通过直接修改 `task.json`、跳过用户交互、子代理代替主会话确认、未登记证据或缺少 disposition 的方式绕过门禁。

## 权威入口

- 阶段流程：`$PDCA_HOME/ontology/process/flow-plan.md`、`$PDCA_HOME/ontology/process/flow-do.md`、`$PDCA_HOME/ontology/process/flow-check.md`、`$PDCA_HOME/ontology/process/flow-act.md`
- 阶段转换：`$PDCA_HOME/ontology/domain/pdca/skill-advance-phase.md`
- 任务拆解：`$PDCA_HOME/ontology/domain/pdca/skill-to-tickets.md`
- 追问与对齐：`$PDCA_HOME/ontology/domain/pdca/skill-grilling.md`
- 证据登记：`$PDCA_HOME/ontology/domain/pdca/skill-register-evidence.md`
- 结论与日志：`write-conclusion`、`write-journal`
- 完整技能索引：`$PDCA_HOME/SKILLS-INDEX.md`
- 环境自检：`python3 "$PDCA_HOME/scripts/pdca-doctor.py" --json`
- 严格任务合约：`$PDCA_HOME/schemas/task.schema.json`
- 能力协议：`$PDCA_HOME/ontology/concept/capability-protocol.md`

阶段流程、本体节点与技能文件是权威来源；本入口只做路由，不复制其全部内容。术语变更同步 `$PDCA_HOME/pdca/CONTEXT.md`，架构级硬决策同步 `$PDCA_HOME/ontology/`（对应本体节点）。

## 沟通与维护约定

- **纠偏重述（re-pitch）**：用户表达未理解、消息未传达到位时，补足缺失上下文后用 `$PDCA_HOME/pdca/CONTEXT.md` 共享语言重新表述，简明优先。
- **路由防谎**：新增、改名或删除技能时，必须运行 `scripts/generate-skills-index.py` 重新生成 SKILLS-INDEX 并核对本入口的路由仍然准确——路由指向不存在或过时的技能即是说谎。
- **git 防护**：对本仓库禁用 `push --force`、`reset --hard`、`clean -f`、`branch -D`、`checkout .` 等破坏性操作；`mv` 任务目录或批量变更前必须确认 `meta.phase == archive` 且转换 receipt 无 rejected——被拒即停，先读原因再动文件。

## 外部项目模式

外部项目使用：

```bash
bash "$PDCA_HOME/scripts/init-external.sh" /path/to/project
```

外部项目的 `AGENTS.md` 通过 `$PDCA_HOME` 引用本管理中心；任务、记录、知识和证据仍写入本仓库。保护外部项目已有说明，不覆盖其原有规则。
