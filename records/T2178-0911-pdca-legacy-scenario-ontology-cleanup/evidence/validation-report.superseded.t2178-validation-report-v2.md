# T2178 Do 验证报告

验证日期：2026-09-11。

## 结果

| 检查 | 命令 | 结果 |
|---|---|---|
| 本体契约 | `python3 scripts/ontology-validate.py --ontology-dir ontology` | exit 0；`OK: ontology 通过本体契约校验` |
| 本体图 | `python3 scripts/ontology_graph.py --root ontology --format summary` | exit 0；nodes 569，edges 1727，islands 0 |
| 技能索引 | `python3 scripts/generate-skills-index.py --root . --check` | exit 0；`valid: true`，asset_count 50 |
| 旧字段/结构扫描 | `rg` 扫描全集中的 scenario_type、scenario type、结构化 scenarios、六场景、6 路由和 A/B/C 路径表达 | exit 1；零命中 |
| 六值控制扫描 | `rg` 扫描六值共现、development/bugfix、非research、research 类任务、场景路由/路径/分类/分流/职责/门禁 | exit 1；零命中 |
| 删除节点引用 | `rg` 扫描四个删除节点 ID 的 active ontology/process/concept/domain/entity/decision/pitfall 引用 | exit 1；零命中 |
| AGENTS 路由 | `rg` 对照 `AGENTS.md` 与 `SKILLS-INDEX.md` 的 flow 和六个命名技能入口 | exit 0；全部目标存在 |
| diff 结构 | `git diff --check` | exit 0；无空白错误 |

## 允许命中

- 工具名称：`skill-research`、`skill-web-research`、`skill-code-review`、`skill-design-it-twice`、`research-report.md`、`review.md`、`design.md`。这些命中只表示工具、方法或产物，并在路由相关正文中明确由 `execution_contract.required_actions`/`work_product` 选择。
- 证据类型：`skill-register-evidence.md` 中的 `documentation` 支持型 kind、`review` evidence subtype 示例，以及 `pdca-evidence.md`/`flow-check.md` 的 review/arch-report 证据说明。
- 普通描述：bug report、设计问题、代码审查、文档内容、测试场景、适用场景等自然语言；不映射职责、阶段行为或门禁。
- 方法名称：`ontology-hybrid-research-topdown` 和 `Hybrid Research→Dev` 表示本体建模方法的来源/方向，不是 task 字段或 Do 路由。
- 历史事实：`ontology/versions/` 中旧节点快照，以及当前并行工作树 `ontology/_index/manifest.jsonl` 中尚未重建的生成索引条目。二者不属于 active 权威节点或本任务声明的核心入口集合；未修改历史版本，也未手改并行生成产物。

## 范围确认

- 未修改 config、scripts、tests、journal、archive 或其他任务。
- 当前任务保持 `meta.phase=do`；未写 conclusion/verdict，未执行 Do→Check。

