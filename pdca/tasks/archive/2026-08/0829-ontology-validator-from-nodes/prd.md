# T0413 PRD：让 ontology-validate.py 运行时读取 ontology-rule-* 节点驱动门禁

- 任务 ID：T0413
- 父任务 / 依赖：T0412（meta-ontology 已建，承载门禁权威）
- 场景类型：development

## 背景与问题

T0412 把本体创建门禁的 6 条规则（AC-1~AC-6）建模为 `ontology/concept/ontology-rule-*` 节点，使"门禁权威"在**概念层**有出处。但 `scripts/ontology-validate.py` 的**实际检查逻辑仍由脚本内硬编码常量驱动**：`TYPE_VOCAB`、`RELATION_KEYS`、`KNOWLEDGE_VOCAB`、`DOMAIN_VOCAB`、`TLS_CONFIG_ID`、属性测试字段名 `testable_signal`、必需关系 `guides/relates_to` 等。节点只是镜像，与脚本逻辑存在漂移风险——改了节点不意味着改了校验行为。

**目标（用户原话：本体才是门禁的权威来源）**：把规则中的"数据型参数"写入 `ontology-rule-*` 节点的结构化 `rule_spec`，让 `ontology-validate.py` 在运行时读取这些参数来**真正执行**检查，使 `ontology/` 节点成为门禁唯一事实源，从源头消除文档/脚本漂移。

## 设计概览（B3：参数化驱动）

`ontology-validate.py` 启动时加载 6 个 `ontology-rule-*` 节点，解析各自 `rule_spec`，构建校验配置并据此执行现有 AC-1b/AC-2/AC-3/AC-4/AC-5/AC-6 及 `composed_of`/`configured_by` 范围检查。原硬编码常量改为从 `rule_spec` 派生；规则节点缺失或 `rule_spec` 非法时明确报错（本体为权威，不允许静默回退）。

### 节点 → rule_spec 映射

| 节点 | rule_spec 字段 | 取代的脚本常量 / 行为 |
|------|----------------|------------------------|
| `ontology-rule-type-controlled` (AC-1) | `allowed_types` | `TYPE_VOCAB`（type 受控词汇）；目录即真理仍由代码执行但依赖 `allowed_types` |
| `ontology-rule-non-dangling` (AC-2) | `reference_relation_keys` + `extra_reference_fields: ["domain"]` | `RELATION_KEYS`（空悬检查遍历的关系键） |
| `ontology-rule-acyclic` (AC-3) | `graph_relation_keys` | `RELATION_KEYS`（建图判无环的关系键） |
| `ontology-rule-attr-testable` (AC-4) | `attribute_test_field: "testable_signal"` | 属性测试覆盖字段名 |
| `ontology-rule-richness` (AC-5) | `knowledge_types` + `required_relations: ["guides","relates_to"]` + `composed_of_range: ["entity","concept"]` | `KNOWLEDGE_VOCAB`、必需关系、`composed_of` range |
| `ontology-rule-guides-range` (AC-6) | `source_types` + `target_types` + `configured_by_target: "ontology:entity/tls-configuration"` | `KNOWLEDGE_VOCAB`(guides 源)、`DOMAIN_VOCAB`(guides 目标)、`TLS_CONFIG_ID`(configured_by range) |

### 自举安全

- 规则节点均为 `type: concept`，不被 AC-4（属性测试）、AC-5/AC-6（知识资产丰富度/范围）约束，仅受 AC-1/AC-2/AC-3 约束且已满足 → 加载 `rule_spec` 早于校验执行，无死锁。
- validator 仅读取规则节点 frontmatter（不含 `rule_spec` 强 schema 校验，已在 T0412 验证安全）。
- 若任一 `ontology-rule-*` 节点缺失或 `rule_spec` 关键字段缺失/类型错，validator 以非零退出并报错，避免"规则被悄悄绕过"。

## 验收条件（AC）

- **AC-1** 在 6 个 `ontology-rule-*` 节点 frontmatter 加结构化 `rule_spec`，字段与上述映射一致；`ontology-validate` 对这些节点自身仍 OK、无环。
- **AC-2** `ontology-validate.py` 启动时加载 `ontology-rule-*` 的 `rule_spec`，构建校验配置并据以执行 AC-1b/AC-2/AC-3/AC-4/AC-5/AC-6 及 `composed_of`/`configured_by` range；硬编码常量被派生取代（允许保留为加载失败的兜底，但默认路径全部来自节点）。
- **AC-3** 自举安全：规则节点缺失/`rule_spec` 非法时 validator 明确报错（非零退出）；现有 `ontology/` 全量仍通过校验、无环、无孤岛。
- **AC-4** 行为不变性：全量既有测试通过——`tests/test_ontology_reason.py`、`tests/test_ontology_induction.py`、`tests/test_pdca_ontology_correct.py`、`tests/test_meta_ontology.py`；`ontology-validate` 对当前 `ontology/` 输出 OK。
- **AC-5** 权威证明：新增 `tests/test_ontology_validator_from_nodes.py`，含用例验证① 修改某 rule 节点 `rule_spec`（如 `allowed_types` 增删一个 type、`knowledge_types` 变更）后 validator 行为随之改变；② 规则节点缺失时 validator 报错。证明行为源自节点而非脚本常量。
- **AC-6** 文档同步：`ontology/README.md` §9 与 `skills/ontology-check` 更新说明"validator 运行时读取 `ontology-rule-*` 节点 `rule_spec` 作为门禁参数唯一来源"；`docs/adr/ADR-0034` 追加 B 方案落地说明（或新建 ADR-0035）。

## 验收标准

- [ ] AC-1：在 6 个 `ontology-rule-*` 节点 frontmatter 加结构化 `rule_spec`，字段与映射表一致；节点自身仍通过 `ontology-validate`（无环）。
- [ ] AC-2：`ontology-validate.py` 启动时加载 `ontology-rule-*` 的 `rule_spec`，据此执行 AC-1b/AC-2/AC-3/AC-4/AC-5/AC-6 及 `composed_of`/`configured_by` range；硬编码常量被节点参数取代。
- [ ] AC-3：自举安全——规则节点缺失/`rule_spec` 非法时 validator 明确报错（非零退出）；现有 `ontology/` 全量仍通过校验、无环、无孤岛。
- [ ] AC-4：行为不变性——`test_ontology_reason.py`/`test_ontology_induction.py`/`test_pdca_ontology_correct.py`/`test_meta_ontology.py` 全量通过；`ontology-validate` 对当前 `ontology/` 输出 OK。
- [ ] AC-5：权威证明——`tests/test_ontology_validator_from_nodes.py` 验证① 修改 rule 节点 `rule_spec` 后 validator 行为随之改变；② 规则节点缺失时 validator 报错。
- [ ] AC-6：文档同步——`ontology/README.md` §9 与 `skills/ontology-check` 说明 validator 运行时读取 `ontology-rule-*` `rule_spec` 为门禁参数唯一来源；`docs/adr/ADR-0034` 追加 B 方案落地说明（或新建 ADR-0035）。

## 非目标（范围边界）

- 不把算法性检查（如 AC-3 的 DFS 环检测）改写为节点内可执行脚本——节点承载**参数**，算法仍在代码内但用节点参数运作（B3，非 B2 全规则引擎）。
- 不改 PDCA 任务流转门禁（`transition-phase.py` 等）；不改变 `ontology/` 其他消费方。

## 风险与缓解

- **风险**：`rule_spec` 与脚本预期不一致导致误报。缓解：AC-5 权威证明测试锁定"节点变更→行为变更"；CI 跑全量校验。
- **风险**：规则节点本身需先通过校验才能被加载，形成隐式依赖。缓解：规则节点为 concept 且已稳定，`rule_spec` 不触发知识资产类检查；加载在全校验前完成。
