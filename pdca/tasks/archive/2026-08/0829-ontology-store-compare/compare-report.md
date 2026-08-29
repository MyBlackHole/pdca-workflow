# T0406 比较分析报告：本体存放写法调研比较

## 0. 结论速览
**推荐方案：兼容吸收（不替换 SSOT v3）。**
保留现有 `pdca.asset/v1` frontmatter + YAML `relations:` 作为机器权威；可选增补 `domain`/`docType`/`tags` 等人读字段；允许正文 `[[wikilink]]` 作为**人类可读增强视图**（非关系来源）；新增 `_meta.yaml` 声明"语义权威 = frontmatter + relations"；补一个 Obsidian 图谱/孤岛检测辅助脚本以满足提案的"可视化"诉求。**不修订 SSOT v3、不改任何现有节点与脚本。**

## 1. 两套写法规范梳理（T0406-1）

### A. SSOT v3（现状，机器权威）
- frontmatter：`schema: pdca.asset/v1`、`id: ontology:<type>/<slug>`、`type` ∈ 受控词汇（domain/entity/concept/process/role/pattern/principle/pitfall/fact/decision）、`layer`、`status`、`summary`。
- 关系：YAML `relations:` 块，`specializes`/`composed_of`/`configured_by`/`guides`/`relates_to`，**受 `ontology-validate` 强制校验**（AC-1 type==目录名；AC-1b 词汇；AC-2 引用非空悬；关系 range；属性格式；GUIDES_RANGE 等）。
- 属性：`attributes: [{name, desc, constraint, testable_signal}]`，承载语义描述与可测信号。
- 目录即真理：`type` 必须等于父目录名。

### B. 用户提案（Markdown 草拟工作法）
- frontmatter：`type: Class|Individual`、`superClass`、`domain`、`docType`、`tags`。
- 关系：正文 `[[路径]]` + 谓语（如 `**继承父类 (subClassOf)**: [[concept/domain-entity]]`）。
- 属性：正文二级列表 `- **名称 (en)**: 数据类型 X`。
- `_meta.yaml` 声明"顶级文件夹仅为人类阅读索引，不参与本体层级"。

## 2. 真实样本标注（T0406-2）
对 `x509-certificate`(entity)、`mtls-handshake-enum-unify`(pattern)、`structured-mtls-failure-diagnostics`(principle)、`pdca`(concept) 在两套写法下的等价表达已分别给出（SSOT 用仓库真实节点；提案风格用 `samples/proposal/*.md` 同概念重写）。两者语义可一一对应，故"表达力"上等价。

## 3. 原型转 OWL/TTL 验证（T0406-3，输出见 `prototype-output.md`）
用 `proto_ontology_to_owl.py` 对 4 个 SSOT 真实节点与 3 个提案风格样本分别生成 TTL，观察映射完整度与脆弱度。

### 关键发现（来自原型实测）
1. **双重表达导致重复/歧义三元组**：提案在 frontmatter `superClass` 与正文 `[[...]] (subClassOf)` 两处表达同一关系，原型同时生成 `rdfs:subClassOf` 与 `pdca:subClassOf` 两条断言。两份来源一旦不一致即语义分裂。
2. **自由文本谓词需归一化**：提案谓词（`subClassOf`/`guidedBy`/`dependsOn`/`certificateChain`）是中文括号里的英文片段，并非受控词汇。直接映射成 `pdca:subClassOf`（错，应为 `rdfs:subClassOf`）、`pdca:guidedBy` 等，产生属性爆炸与语义歧义，必须额外做"谓词→OWL 属性"归一化层。
3. **属性仅类型、丢失取值与描述**：提案属性行只有"数据类型 X"，无取值/描述；对应 SSOT 的 `desc`/`testable_signal` 在提案里无处安放，映射后数据属性值为空（`""^^xsd:string`），语义信息损失。
4. **拼写错误静默断图**：wikilink 路径拼错不会被任何现有校验捕获（SSOT 的 AC-2 引用空悬检查依赖 `relations` 字段，对正文 wikilink 无效）。

## 4. 五维度对比（AC-1）

| 维度 | SSOT v3 | 用户提案 | 胜出 |
|------|---------|----------|------|
| 机器可校验性 | 高（`ontology-validate` 强制 type 词汇/引用/range/属性格式） | 无内置校验，需另建；wikilink 错拼静默 | SSOT |
| 人类可读性 | 较弱（关系藏在 YAML，目录耦合） | 强（文件夹仅归档、正文 wikilink 散文化、Obsidian 开箱图谱） | 提案 |
| OWL/RDF 升级路径 | 无损、直接（受控谓词→owl:ObjectProperty；属性带描述） | 需谓词归一化 + 类型补全，且存在双重表达/空值风险 | SSOT |
| 迁移成本 | 已落地，0 成本 | 需重写全部节点（破坏 T0402 record identity、T0405 PDCA 元本体、`ontology-validate`/`transition-phase` 逻辑），巨大返工 | SSOT |
| 工具生态/可视化 | 需自建图导出（ADR-0031 已规划 `pdca-graph`） | Obsidian/Foam 开箱图谱、孤岛可视 | 提案 |

## 5. 推荐方案与理由（AC-3）
**兼容吸收**：用户提案的"精神"（先人后机、MD 草稿、脚本升华、可视化自检）全部可在 SSOT 框架内实现，且不需推翻现有契约：
- 机器权威不变：`pdca.asset/v1` + `relations` 仍为唯一语义来源（保障可校验性、无损 OWL 升级、零迁移）。
- 人读增强可选：frontmatter 增 `domain`/`docType`/`tags` 便于过滤；正文 `[[wikilink]]` 允许作为 relations 的**人类可读镜像视图**（明确标注"派生、非来源"，并加 lint 防止与 relations 漂移）。
- `_meta.yaml` 改写：不宣称"文件夹不参与层级"，而是"文件夹为人类阅读索引；语义权威 = frontmatter + relations"。
- 可视化：新增 `scripts/ontology_graph.py`（或扩 ADR-0031 的 pdca-graph）输出 Obsidian 兼容图谱 + 孤岛检测，满足提案的可视化诉求。

**风险与边界**
- 若正文 wikilink 与 `relations` 并存且无同步校验，会重演"双重表达"分裂 → 必须规定 relations 为唯一来源，wikilink 为派生视图（或干脆只在 README/指南中示例，不在节点正文强制）。
- 直接替换 SSOT 的代价（迁移 + 重写校验/流程 + 破坏既有资产）远高于收益，且无证据显示提案在可校验性/OWL 升级上更优，故不推荐替换。

## 6. 不动 SSOT 声明（AC-5）
本报告与 `ONTOLOGY_GUIDE.draft.md` 均为**建议与草案**，不改变：
- `task.schema.json` / `ontology-validate.py` / `transition-phase.py` / `ontology_reason.py` / `ontology_gate.py`；
- 任何现有 `ontology/**` 节点（含 T0405 PDCA 元本体、T0402 迁移资产）；
- `ontology/README.md`（SSOT v3 语义主干）继续作为权威。
若未来决定采纳指南草案，应另立任务/ADR，而非在本任务内实施。
