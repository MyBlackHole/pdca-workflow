# ADR-0035: 校验器运行时读取 ontology-rule-* 节点作为门禁参数唯一来源

日期: 2026-08-29
状态: Accepted

## 背景

ADR-0034（T0412）把本体创建门禁的 AC-1~AC-6 建模为 `ontology/concept/ontology-rule-*` 节点，使门禁在**概念层**有出处；但 `scripts/ontology-validate.py` 的**实际检查仍由脚本内硬编码常量驱动**（`TYPE_VOCAB`、`RELATION_KEYS`、`KNOWLEDGE_VOCAB`、`DOMAIN_VOCAB`、`TLS_CONFIG_ID`、属性测试字段名、必需关系等）。节点只是镜像，与脚本逻辑存在漂移风险——改了节点不意味改了校验行为。用户明确：**本体才是门禁的权威来源**（B 方案 / B3 参数化驱动）。

## 决策

1. 在 6 个 `ontology-rule-*` 节点的 frontmatter 增加结构化 `rule_spec`，分别承载门禁参数：
   - `ontology-rule-type-controlled`：`allowed_types`（受控类型词表）
   - `ontology-rule-non-dangling`：`reference_relation_keys`（空悬检查遍历的关系键）+ `extra_reference_fields: [domain]`
   - `ontology-rule-acyclic`：`graph_relation_keys`（建图判无环的关系键）
   - `ontology-rule-attr-testable`：`attribute_test_field: testable_signal`
   - `ontology-rule-richness`：`knowledge_types` + `required_relations` + `composed_of_range`
   - `ontology-rule-guides-range`：`source_types` + `target_types` + `configured_by_target`
2. `ontology-validate.py` 启动时加载 6 个 `ontology-rule-*` 节点的 `rule_spec`，据此构建校验配置并真正执行 AC-1b/AC-2/AC-3/AC-4/AC-5/AC-6 及 `composed_of`/`configured_by` 范围检查；原硬编码常量被节点参数取代。
3. **本体为权威，不允许静默回退**：任一规则节点缺失或 `rule_spec` 非法时，校验器直接 `sys.exit` 报错退出；不保留"加载失败回退到硬编码常量"的路径。
4. 自举安全：规则节点均为 `type: concept`，不触发知识资产类检查（AC-4/AC-5/AC-6），仅受 AC-1/AC-2/AC-3 约束且已满足；加载 `rule_spec` 早于全校验执行，无死锁。`rule_spec` 为政制 frontmatter 字段，校验器不强校验额外字段，故不会自举失败。
5. 测试证据：`tests/test_ontology_validator_from_nodes.py` 含用例证明① 修改某 rule 节点 `rule_spec`（如 `allowed_types` 增删类型）后校验行为随之改变；② 规则节点缺失时校验器报错。证明行为源自节点而非脚本常量。

## 影响

- 改门禁规则（如新增受控类型、调整知识资产范围）只改 `ontology-rule-*` 节点的 `rule_spec`，`ontology-validate.py` 行为自动跟随——文档/脚本漂移从源头消除。
- `ontology/README.md` §9 与 `skills/ontology-check` 已更新为"节点是门禁参数唯一事实源"，并声明规则节点缺失即报错。
- 风险：若 `rule_spec` 与节点正文描述不一致，以后者（文档）为准；`rule_spec` 是唯一机器语义源。
- 衔接 T0412/T0413：本 ADR 是 T0413 的落地授权；ADR-0034 的 A 方案（概念层权威）升级为 B 方案（参数运行时驱动）。
