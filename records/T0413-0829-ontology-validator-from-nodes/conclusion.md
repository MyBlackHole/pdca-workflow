# T0413 结论（Check 阶段）

- record: T0413-0829-ontology-validator-from-nodes
- 阶段结论：让 `ontology-validate.py` 运行时读取 6 个 `ontology-rule-*` 节点的 `rule_spec` 作为门禁参数唯一事实源，受控类型词表/关系键/属性测试字段/知识资产类型/必需关系/范围约束等从硬编码常量改为由节点驱动；规则节点缺失或 `rule_spec` 非法即报错（本体为权威，不静默回退）。`validate-convergence` 通过（`valid: true`），`ontology-validate` 无环、无孤岛。

## 验收对照
| AC | 内容 | 证据 |
|----|------|------|
| AC-1 | 6 个 `ontology-rule-*` 节点 frontmatter 加结构化 `rule_spec`（allowed_types / reference_relation_keys+extra / graph_relation_keys / attribute_test_field / knowledge_types+required_relations+composed_of_range / source_types+target_types+configured_by_target） | `t0413-rule-type-controlled` … `t0413-rule-guides-range` |
| AC-2 | `ontology-validate.py` 启动时加载 `rule_spec` 构建校验配置并据以执行 AC-1b/AC-2/AC-3/AC-4/AC-5/AC-6 及 composed_of/configured_by range；硬编码常量被节点参数取代 | `t0413-validator` |
| AC-3 | 自举安全：规则节点为 concept 类型不触知识资产检查；加载早于全校验；缺失/非法即 `sys.exit` 报错 | `t0413-validator` `t0413-test` |
| AC-4 | 行为不变性：现有 `ontology/` 仍通过 `ontology-validate`（OK）；相关测试全绿（36 项） | `t0413-validate` |
| AC-5 | 权威证明：`tests/test_ontology_validator_from_nodes.py` 5 用例证明① 修改 rule 节点 `rule_spec`（allowed_types 增删）→ 校验行为随之改变；② 规则节点缺失 → 校验器报错 | `t0413-test` |
| AC-6 | 文档同步：`ontology/README.md` §9、`skills/ontology-check` 更新为"节点是门禁参数唯一事实源"；`docs/adr/ADR-0035` 记录决策 | `t0413-readme` `t0413-skill` `t0413-adr` |

`validate-convergence`：`valid: true`。

## 设计要点
- **节点是门禁权威**：原 `TYPE_VOCAB`/`RELATION_KEYS`/`KNOWLEDGE_VOCAB`/`DOMAIN_VOCAB`/`TLS_CONFIG_ID` 等常量改为从 `rule_spec` 派生；改规则只改节点，校验行为自动跟随，从源头消除文档/脚本漂移。
- **不静默回退**：`load_rule_specs` 在规则节点缺失或 `rule_spec` 非 dict 时直接 `sys.exit`，确保本体权威不可被绕过。
- 自举无死锁：规则节点为 `concept`，不触发 AC-4/AC-5/AC-6；`rule_spec` 为政制 frontmatter 字段，校验器不强校验额外字段。

## Verdict
- outcome: **confirmed**
