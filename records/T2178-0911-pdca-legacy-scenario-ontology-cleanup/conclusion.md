---
schema: pdca.asset/v1
id: T2178-0911-pdca-legacy-scenario-ontology-cleanup
phase: check
source_ids: [t2178-core-authority-inventory-v2, t2178-authority-change-snapshot-v2, t2178-validation-report-v3, t2178-convergence-map-v5]
---

# T2178 核心旧场景控制语义清理结论

## 上下文

T2175 已确认三个专业职责与四字段执行契约，但活跃核心入口仍残留 `scenario_type`、六场景、A/B/C 和“6 路由”控制语义。T2178 只清理本体与权威路由文档，不修改配置、Python runtime、测试或历史记录。

## 假设与结果

假设成立：旧词可以按控制语义、工具名称、证据类型、普通描述和历史事实分类，只删除承担任务分类、执行路径、阶段行为或门禁控制的用法，而保留工具和业务表达。

首次实现的入口全集漏掉 `README.md`、`ontology/README.md` 和 `pdca/CONTEXT.md`，被主协调器的 `ontology_conformance_verification` 驳回。修正后，四个显式入口、活跃流程/概念/PDCA domain skill 节点和四个阶段实体均纳入扫描，旧控制语义为零命中。

## 分析

- **AC-1** ✅ 已产出核心权威入口全集，并逐项区分控制语义、工具名称、证据类型、普通描述和历史事实。（t2178-core-authority-inventory-v2, t2178-validation-report-v3）
- **AC-2** ✅ `AGENTS.md` 和根 README 已改为按 `meta.ontology_role` 与四字段 `meta.execution_contract` 执行，不再声明 `meta.scenario_type` 路由。（t2178-authority-change-snapshot-v2, t2178-validation-report-v3）
- **AC-3** ✅ Plan、Do、Check、Act、阶段概念及 Do 实体不再用六场景、A/B/C 或“6 路由”控制阶段行为。（t2178-core-authority-inventory-v2, t2178-authority-change-snapshot-v2, t2178-validation-report-v3）
- **AC-4** ✅ 分诊、用户路由、上下文编排和关联技能统一输出三个专业职责与四字段执行契约，旧请求词不再映射为 ontology_role 或执行路径。（t2178-authority-change-snapshot-v2, t2178-validation-report-v3）
- **AC-5** ✅ 四个失去当前权威意义的旧节点已删除，活跃本体和流程无引用，未创建 alias、redirect 或兼容节点。（t2178-core-authority-inventory-v2, t2178-authority-change-snapshot-v2, t2178-validation-report-v3）
- **AC-6** ✅ `research`、`web-research`、`code-review`、`design-it-twice` 等仅作为执行契约可选择的工具或产物名称保留，不参与生命周期控制。（t2178-core-authority-inventory-v2, t2178-authority-change-snapshot-v2, t2178-validation-report-v3）
- **AC-7** ✅ 扩展后的核心入口全集中，旧字段、六值分组、A/B/C 路由、“6 路由”及已删除节点活跃引用均为零命中；允许项已逐类说明。（t2178-core-authority-inventory-v2, t2178-validation-report-v3）
- **AC-8** ✅ `ontology-validate`、本体图 0 孤岛、技能索引、收敛校验和 `git diff --check` 全部通过。（t2178-validation-report-v3, t2178-convergence-map-v5）

## 失败纠正

首次扫描把“active pdca.asset 节点”误当成完整核心入口集合，遗漏了三个没有相同 frontmatter 但实际承担当前路由或术语权威的文档。修正后的清单显式列出四个路由入口，避免再次以文件格式代替职责边界。

## 适用边界

- 历史 records、journal、archive 和 `ontology/versions/` 中的旧词保持不可变，不代表当前控制模型。
- `ontology/_index/manifest.jsonl` 仍有一个已删除节点的并行生成旧索引条目；该文件不是 active 本体节点或路由权威，本任务未覆盖其他工作所有者的生成工件。它不是兼容节点，但索引所有者后续重建时应自然消失。
- 配置、Python runtime 和测试仍可能消费旧字段，须由后续独立 `ontology_projection` PDCA 处理；本结论不宣称 runtime 迁移完成。

## 下一轮建议

建立 runtime `ontology_projection` 任务，把三个专业职责、四字段执行契约、`agent.spawn` fail-closed 和当前任务恢复规则投射到 Schema、配置、Python 实现及完整测试夹具。

## 判定

- outcome: confirmed
- reason: AC-1 至 AC-8 均由当前有效证据覆盖，首次入口集合遗漏已纠正，活跃核心权威入口旧控制语义零命中且本体结构校验通过。
- verdict_id: V-T2178-20260911
- at: 2026-09-11T16:17:23+08:00

## 本体沉淀

- disposition: ontology
- 建模锚点：`ontology:concept/pdca`。
- 更新节点：`ontology:process/flow-plan`、`ontology:process/flow-do`、`ontology:process/flow-check`、`ontology:process/flow-act`、`ontology:concept/capability-protocol` 及其关联的分诊、路由和阶段实体节点。
- 删除节点：`ontology:concept/pdca-scenario-boundary-rule`、`ontology:concept/scenario-research-first-gate`、`ontology:concept/tickets-leaf-exemption`、`ontology:decision/t2148-bugfix-specialization`；不保留 alias、redirect 或兼容入口。
- 固化规则：核心行为只由 `meta.ontology_role` 与 `meta.execution_contract` 控制；场景词、工具名和产物名不得承担生命周期或阶段路由语义。
