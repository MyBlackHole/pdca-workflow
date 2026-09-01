# 本体深度融合：拆分×测试×树形执行×全任务知识闭环

## 背景

当前本体在任务拆分与测试中为**顾问式**：`to-tickets#3.5` 关系树驱动仅在 PRD 含`## 拆分映射`且`meta.ontology_fragment`非空时触发，`testing-strategy` 与 `testable_signal` 为文档提示未自动骨架化，`composed_of` 树仅少数实体有导致 WBS 不饱满，全任务知识闭环仅`research`强制，其余可空`fragment`通关。本任务将本体从可选推为默认，使任意任务皆可通过本体表达、叶→根执行、事事沉淀知识。

## 目标

- 拆分：本体对齐为默认路径，叶→根 WBS 由本体 `composed_of/specializes` 树驱动，依赖边自动推导
- 测试：`attributes.testable_signal` 三模式（属性断言/契约测试/收敛验证）自动派生可执行测试骨架
- 结构：本体按 `ontology-modular-reference` 独立拆分，清单透传，扇出而非串联，链路自然可控
- 闭环：任意 `scenario_type` 任务强制本体表达与产出，Act 统一沉淀，证据回链本体

## 范围

- 输入：现有 `ontology/` 351节点图谱、`skill-to-tickets`、`skill-testing-strategy`、`ontology_tree_split`、`ontology-clash-check`、`compute-frontier`、`ontology_graph`、`ontology-validate`
- 输出：4个硬化子系统 + 1个集成验证，形成叶→根依赖树；新增/补强本体节点与脚本，门禁全绿
- 不做：不引入图数据库，不改 `task.schema.json` 结构，不强制历史任务补 `fragment`

## 功能需求

1. 拆分门禁硬化：`to-tickets` 默认校验 `ontology_fragment`，无映射告警，有 fragment 必跑 `ontology_tree_split`，`clash-check` 阻断保留，`task_identity` 继承强化
2. 测试派生硬化：新增 `scripts/ontology_test_scaffold.py`，输入本体节点 id，输出三模式测试骨架与映射表，与 `testing-strategy` 强绑定
3. 树形执行：补齐核心领域 `composed_of` 边，父聚合子，部分-整体语义；`ready-set/batches` 叶并行根串行，提供 `dot` 可视化
4. 知识闭环：任意任务 `meta.ontology_anchor` 默认 `ontology:concept/pdca-task`，`meta.ontology_fragment` 非空为默认豁免需理由；Act `meta.disposition` 含 `ontology:` 或显式 `records-only`，否则 `archive` 拒收；`auto_induce` 提示反哺
5. 独立体现：按 `ontology-modular-reference` 四条分流（≥2复用/≥3 attributes/维度正交/方法论类）判定独立 vs 内联，清单透传不单独立节点

## 非功能需求

- 门禁零回退：`ontology-validate` 与 `compute-frontier` 必须通过，`islands=0`
- 兼容性：旧任务无 `fragment` 默认不阻断新门禁，仅新任务生效
- 可观测：`ontology_graph --format summary/dot` 与 `compute-frontier` 输出机器可读

## 验收标准

- [ ] AC-1 拆分默认本体对齐：`to-tickets` 在有 `meta.ontology_fragment` 时默认执行 `ontology_tree_split`，无 `## 拆分映射` 时告警而非静默跳过，`ontology-clash-check` 仍为阻断门禁，`task_identity` 自动继承 `fragment/node_type`
- [ ] AC-2 测试三模式自动骨架：`scripts/ontology_test_scaffold.py --node <id>` 能按 `attributes.testable_signal` 三模式生成 `tests/test_<slug>.py` 骨架与 `scaffold-map.json`，且与 `skill-testing-strategy` 文档互链
- [ ] AC-3 树形执行与依赖推导：WBS 父节点 `composed_of` 聚合子实体，`ontology_tree_split` 输出叶→根 `dependencies`，`compute-frontier` 算出 `ready-set/batches` 叶可并行根等待，`ontology_graph --format dot` 可导出树图
- [ ] AC-4 全任务知识闭环：任意 `scenario_type` 任务均可通过 `ontology_anchor/fragment` 表达，Act 阶段 `meta.disposition` 必须含 `ontology:` 或显式 `records-only` 理由，否则 `transition-phase.py → archive` 被 `ontology_gate` 拒收
- [ ] AC-5 本体独立与链路可控：新增知识按 `ontology-modular-reference` 独立判定，清单透传不单独立节点，单任务引用本体数通常≤3，`ontology_graph` 检查 `0 islands` 且强引用均存在
- [ ] AC-6 本体校验全绿：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues，`python3 scripts/ontology_graph.py --format summary` `islands:0`，`python3 scripts/compute-frontier.py` 对拆分后 DAG 校验 `valid:true`
- [ ] AC-7 收敛闭环可验证：`records/<record>/convergence.json` 逐条回链 `meta.convergence → PRD AC-N → evidence`，`validate-convergence.py` 报告 `valid:true` 且每条 AC 有非 map evidence 覆盖

## 关联本体节点

```
ontology:entity/ontology-deep-integration
ontology:entity/ontology-deep-integration-split
ontology:entity/ontology-deep-integration-test
ontology:entity/ontology-deep-integration-tree
ontology:entity/ontology-deep-integration-knowledge
ontology:domain/ontology-deep-integration-overview
ontology:pattern/testable-signal-to-test-derivation
ontology:pattern/ontology-modular-reference
ontology:domain/ai-efficiency-ticket-dag-ready-set
ontology:concept/pdca-task
ontology:concept/knowledge-provenance
```

## 拆分映射

- 拆分门禁硬化 -> ontology:entity/ontology-deep-integration-split
- 测试派生硬化 -> ontology:entity/ontology-deep-integration-test
- 树形执行与依赖推导 -> ontology:entity/ontology-deep-integration-tree
- 全任务知识闭环 -> ontology:entity/ontology-deep-integration-knowledge
- 集成验证与回归 -> ontology:entity/ontology-deep-integration

## 风险与对策

- 风险：`composed_of` 目标类型越界被 `ontology-validate` 判 `COMPOSED_OF_RANGE` 失败。对策：WBS 树仅用 `entity/concept` 类型，`domain` 知识通过 `relates_to` 关联
- 风险：`fragment` 指向大目录导致 `ontology-ready` 检查过重。对策：`fragment` 默认指向 `ontology`，但 `ontology_tree_split` 支持 `--ontology-dir` 聚焦子目录
- 风险：泛化 `testable_signal` 无法派生骨架。对策：复用 `testable-signal-to-test-derivation` 的动词+对象+判定结构校验，拒绝泛化

## 开放问题

- 是否将 `ontology_tree_split` 的“有 fragment 必跑”设为硬阻断（缺映射即失败）还是告警+回退章节拆分？本 PRD 取告警+默认跑，缺映射时报错提示补 `## 拆分映射`
