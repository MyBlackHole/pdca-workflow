# ADR-0030: 知识资产全部物理归并至 ontology/

日期: 2026-08-29
状态: Accepted

## 背景

PDCA 知识管理需要把"按主题（topic）"存放的知识重构为"按完整本体"组织。核心决策点：四层模型（Evidence / Experience / Knowledge / Skill）下的资产在重构中如何归并？

- 方案 A（保守）：仅可复用层（Knowledge / Skill）物理迁移到 `ontology/<type>/`；单次层（Evidence / Experience）留在 `records/<record>/` 仅加标签。
- 方案 B（采纳）：四层资产全部物理归并到 `ontology/` 统一按本体组织；PDCA 机制层（`flows/`、`skills/`、`task.json`）不动。

## 决策

采用**方案 B（全部物理归并）**：`knowledge/` 全部 + `records/*/evidence/`、`experience.md` 物理迁入 `ontology/`；`flows/`、`skills/`、`task.json` 等 PDCA 机制层保持不动。

理由：用户要求"完整本体表达"，跨四层统一按本体组织，避免"ontology + records 残留"双层割裂导致的检索与复用断裂；且本体关系树需覆盖经验/证据层才能完整支持任务分解。

## 影响

- 破坏 `records/<record>/evidence|experience.md` 与具体任务的物理绑定。
- `record identity` 不可变约束需以新方式满足：被迁资产在新位置 frontmatter 保留 `source_task: <record>` 回链；`task.json` 的 `meta.record` 指向新 `ontology/` 路径；保留 `records/<record>/` 空壳 + redirect 说明，保证历史引用不失效（详见 design.md §9）。
- 检索 / P5 注入逻辑改为基于 `ontology/` 路径。
- 风险：来源边可追溯性依赖 `source_task` 字段而非物理位置，需在 `ontology-validate` 中强制该校验。
- 此为不可逆架构决策，后续任务不得回退到双层存放。
