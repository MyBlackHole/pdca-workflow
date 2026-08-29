# T0413 对话日志

## Plan 阶段
- 用户确认需要 B 方案：让 `ontology-validate.py` 运行时读取 `ontology-rule-*` 节点驱动门禁（消除文档/脚本漂移）。经 triage 澄清深度，用户明确"本体才是门禁的权威来源" → 选定 B3 参数化驱动。
- 写 prd.md（AC-1 节点加 rule_spec、AC-2 validator 读节点、AC-3 自举安全、AC-4 行为不变、AC-5 权威证明测试、AC-6 文档同步），用户 final_confirmation 确认进入 Do。

## Do 阶段
- 在 6 个 `ontology-rule-*` 节点 frontmatter 加结构化 `rule_spec`（allowed_types / reference_relation_keys+extra / graph_relation_keys / attribute_test_field / knowledge_types+required_relations+composed_of_range / source_types+target_types+configured_by_target）。
- 改 `scripts/ontology-validate.py`：新增 `load_rule_specs`，启动时从节点读取参数并据以执行 AC-1b/AC-2/AC-3/AC-4/AC-5/AC-6 及范围检查；原硬编码常量被派生取代；规则节点缺失/`rule_spec` 非法即 `sys.exit`。
- 新增 `tests/test_ontology_validator_from_nodes.py` 5 用例，证明"修改 rule 节点 rule_spec → 校验行为随之改变"与"规则节点缺失即报错"。
- 更新 `ontology/README.md` §9、`skills/ontology-check`、`docs/adr/ADR-0035`。
- 校验：ontology-validate OK（无环）、36 项相关测试通过、validate-convergence valid:true、route 自检 ok；登记 12 条证据，进入 Check。

## Check 阶段
- 写 conclusion.md，逐 AC 回链证据；verdict=confirmed。
- 用户 check_confirmation 确认，进入 Act。

## Act 阶段
- 知识决策：成果沉淀于 ontology 节点 + 脚本 + ADR-0035，不产孤立 knowledge/ 文件（knowledge_decision: skipped）。
- disposition=projected（B 方案机制可推广到其它治理门禁）。
- 写 journal 当日摘要，归档任务目录。
