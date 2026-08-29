# PRD：采纳 ONTOLOGY_GUIDE（T0407）

## 背景
T0406 调研比较结论：**兼容吸收**——保留 `pdca.asset/v1` frontmatter + YAML `relations:` 为机器权威，吸收用户提案"先人后机 / 可视化 / 脚本升华"精神；正文 `[[wikilink]]` 作为派生视图；`_meta.yaml` 声明语义权威；补图谱/孤岛检测脚本满足可视化诉求。**不修订 SSOT v3、不改现有节点语义**。

本任务将 T0406 的 `ONTOLOGY_GUIDE.draft.md` 正式落地为 `ontology/ONTOLOGY_GUIDE.md` 与 `ontology/_meta.yaml`，并新增 `scripts/ontology_graph.py`，以及给若干样本节点补可选人读字段。

## 目标
- 在 `ontology/` 根目录提供权威的 `ONTOLOGY_GUIDE.md` 与 `_meta.yaml`，明确"语义权威 = frontmatter + relations"。
- 提供 `scripts/ontology_graph.py`：从 frontmatter+relations 导出 Obsidian 兼容图谱并检测孤岛节点。
- 给若干现有样本节点补 `domain`/`docType`/`tags` 可选字段（人读增强，不改变机器语义、不破坏 `ontology-validate`）。
- 起草 ADR-0033 记录本次采纳决策。

## 范围
- **包含**：`ontology/ONTOLOGY_GUIDE.md`、`ontology/_meta.yaml`、`scripts/ontology_graph.py`、样本节点补字段、`docs/adr/ADR-0033-ontology-guide-adoption.md`、验证与证据登记。
- **排除**：不修改 `task.schema.json` / `ontology-validate.py` / `transition-phase.py` / `ontology_reason.py` / `ontology_gate.py`；不改变任何现有节点的 `type`/`relations`/`id`（仅追加可选字段）；不采用用户原提案的 `Class/Individual`+`superClass`+wikilink-as-source 体系。

## 非目标
- 不做 SSOT v3 的结构性修订。

## 验收标准
- [ ] AC-1: `docs/ONTOLOGY_GUIDE.md` 落地（正式版，去除 DRAFT 标注）：含先人后机理念、frontmatter 身份规范、relations 关系规范、attributes 属性规范、concept/ 类型字典说明、_meta.yaml 说明、升华脚本路径、与原提案差异表；明确语义权威=frontmatter+relations。（注：因 `ontology-validate` 扫描 `ontology/**.md` 并要求节点 frontmatter，指南文档按本体论合规方案置于 `docs/` 而非 `ontology/` 内，避免破坏校验门禁；`ontology/_meta.yaml` 仍为 `.yaml` 不被扫描，留于 `ontology/` 根。）
- [ ] AC-2: `ontology/_meta.yaml` 落地，声明"顶级文件夹为人类阅读索引；语义权威 = 各 .md 的 pdca.asset/v1 frontmatter + YAML relations；正文 wikilink 为派生视图，非关系来源"。
- [ ] AC-3: `scripts/ontology_graph.py` 新增：读取 `ontology/**.md` 的 frontmatter+relations，导出 Obsidian 兼容图谱（节点+互链），并输出孤岛节点清单（无 relations 连线的节点）；脚本可独立运行。
- [ ] AC-4: 给 ≥3 个现有样本节点（须含 `x509-certificate` 与至少 1 个 `pdca-*` 元本体节点）补 `domain`/`docType`/`tags` 可选字段，且 `ontology-validate` 仍通过（type==目录名等不变）。
- [ ] AC-5: `docs/adr/ADR-0033-ontology-guide-adoption.md` 起草，记录采纳兼容吸收方案、_meta.yaml 语义权威声明、明确不变更 SSOT v3。
- [ ] AC-6: `ontology-validate` 与既有测试（`test_ontology_reason.py`、`test_ontology_induction.py`）无回归；在 `records/T0407-0829-ontology-guide-adopt/` 登记证据并写 convergence map。

## 风险
- `ONTOLOGY_GUIDE.md` 与既有 `ontology/README.md`（SSOT v3 语义主干）表述可能重叠，需在指南中明确二者关系（README 为权威契约，指南为使用约定）。
- 给样本节点补字段若误改 `type`/`id`/`relations` 会破坏 `ontology-validate`，须只追加可选字段。
