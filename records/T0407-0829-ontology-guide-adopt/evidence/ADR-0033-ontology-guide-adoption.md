# ADR-0033: 采纳 ONTOLOGY_GUIDE（兼容吸收方案）

日期: 2026-08-29
状态: Accepted

## 背景

T0406 调研比较了用户提案的"基于 Markdown 的本体草拟工作法"（`type: Class/Individual` + `superClass` + 正文 `[[wikilink]]` + `_meta.yaml` 声明"文件夹不参与层级"）与现有 SSOT v3（`pdca.asset/v1` frontmatter + 受控词汇 + YAML `relations:` + `ontology-validate`）。结论为**兼容吸收**：保留 SSOT v3 为机器权威，吸收其"先人后机 / 可视化 / 脚本升华"精神。本 ADR 记录将指南落地为 `docs/ONTOLOGY_GUIDE.md` 的采纳决策及一项关键约束。

## 决策

1. **指南落点（本体论合规）**：`ONTOLOGY_GUIDE.md` 置于 `docs/ONTOLOGY_GUIDE.md`，**不放入 `ontology/` 目录内**。原因：`ontology-validate` 扫描 `ontology/**.md` 并对每个文件强制要求 `pdca.asset/v1` frontmatter 与 `type==目录名`；根级 `.md` 无法满足（根目录不是类型子目录），会破坏校验门禁。指南是文档而非本体节点，故不应作为 `ontology/` 资产。
2. **`_meta.yaml` 留 `ontology/` 根**：其为 `.yaml` 不被 `.md` 扫描器覆盖，合法；声明"顶级文件夹为人类阅读索引；语义权威 = frontmatter + relations；正文 wikilink 为派生视图"。
3. **语义权威不变**：`pdca.asset/v1` frontmatter + YAML `relations:` 仍为唯一事实源；正文 `[[wikilink]]` 仅作派生视图，关系变更必须先改 `relations`。
4. **可视化脚本**：新增 `scripts/ontology_graph.py`，读 frontmatter+relations 导出 Obsidian 兼容图谱并检测孤岛节点，弥补纯 wikilink 无法被机器校验的短板。
5. **可选人读字段**：现有节点可追加 `domain`/`docType`/`tags` 可选 frontmatter 字段（人读增强），不改变机器语义、不破坏 `ontology-validate`。
6. **不变更 SSOT v3**：不修改 `task.schema.json` / `ontology-validate.py` / `transition-phase.py` / `ontology_reason.py` / `ontology_gate.py`；不采用用户原提案的 `Class/Individual`+`superClass`+wikilink-as-source 体系。

## 影响

- 开发者写/读本体以 `docs/ONTOLOGY_GUIDE.md` 为使用约定、`ontology/README.md` 为契约权威，二者冲突以 README 为准。
- `ontology/` 目录保持纯节点资产，`ontology-validate` 门禁不被指南文档干扰。
- `scripts/ontology_graph.py` 提供图谱与孤岛自检，可在 CI 中作为可视化健康度检查（孤岛数=0 为健康信号）。
- 风险：若未来误将非节点 `.md` 放入 `ontology/`，`ontology-validate` 会立即报错，作为安全网。
- 衔接 T0406：本 ADR 是 T0406 推荐方案的落地授权。
