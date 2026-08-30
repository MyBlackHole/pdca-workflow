# AC-2 证据：任务拆分本体感知（to-tickets + 冲突检测）

## 改动
- 新增 `scripts/ontology-clash-check.py`：`find_clashes(root, candidates)` 扫描 `ontology/<type>/<slug>.md` 节点 id（含 frontmatter `id` 别名），对候选 slug/标题做归一化匹配，报告与既有本体节点重名。仅提示、不阻断（退出码恒 0）。
- `skills/to-tickets/SKILL.md`：步骤 3 新增「本体一致性预检」，调用 `ontology-clash-check.py`；步骤 4 的创建命令提示传入 `--ontology-fragment`/`--ontology-node-type`（并说明 `task_identity.py` 已自动继承父值）；Rules 增加继承规则。

## 验证
- 新增 `tests/test_ontology_clash.py`（3 用例：现有节点命中 / 带日期前缀 slug 命中 / CLI 报告），全部通过。详见 `ev-tests.log`。
