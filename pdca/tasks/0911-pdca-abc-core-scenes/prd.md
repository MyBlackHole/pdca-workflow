# PDCA 核心场景 A/B/C 收敛实施

## 背景

T2156 已确认：核心场景只保留 A/B/C，规范名称为 B“本体建模”、A“本体实现”、C“本体验证”；六个旧 `scenario_type` 不保留兼容层，具体工具差异由 skill/tool 路由表达。

当前 `ontology/concept/pdca.md`、`ontology/process/flow-do.md`、`schemas/task.schema.json` 及路由检查脚本仍以六值 `scenario_type` 为核心字段，造成权威文档、schema 和执行门禁不一致。

## 范围

- 修改 `ontology/concept/pdca.md` 的核心名称和场景分层说明。
- 修改 `ontology/process/flow-do.md`，以 A/B/C 为核心路由，以 skill/tool route 表达具体执行差异。
- 将任务 schema 的核心场景字段收敛为 A/B/C，并同步 transition、task identity、scenario 检查、研究结算和相关 fixture。
- 清理旧六值作为核心路由的代码分支，不提供兼容读取。

排除：不重写历史归档任务数据；不扩展领域本体；不改变 PDCA 四阶段门禁语义。

## 验收标准

- [ ] AC-1: `pdca.md` 使用“本体建模/本体实现/本体验证”，明确 A/B/C 是唯一核心场景，保留 B→A→C。
- [ ] AC-2: `flow-do.md` 与 task schema 以 A/B/C 为核心路由，skill/tool route 明确映射三类执行差异。
- [ ] AC-3: 生产脚本和门禁不再把六个旧值作为核心字段或兼容分支，任务 identity、transition、场景检查和研究结算均使用 A/B/C。
- [ ] AC-4: 新增/更新回归测试覆盖 A/B/C 合法性、路由映射和旧六值拒绝；ontology/schema/相关测试通过。

## 关联本体

`ontology:pattern/pdca-core-scene-layering`

## 实施边界

采用一次性迁移：旧六值不兼容读取。若历史任务需要继续审计，由不可变 record 和归档文档保留事实，不在生产 schema 中保留旧分支。
