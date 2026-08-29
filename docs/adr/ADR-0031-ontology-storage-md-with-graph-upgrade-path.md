# ADR-0031: 本体存储选型 — md 优先，保留图数据库升级路径

日期: 2026-08-29
状态: Accepted

## 背景

本体（ontology）作为知识库的语义主干，其**承载方式**需要选型：是用当前 `ontology/` 下的 markdown 文件，还是用网络资料推荐的生产级图数据库？

网络调研结论（一致）：
- 知识图谱 / 本体的生产级承载几乎都推荐**图数据库**：Neo4j property graph（最主流，设计简单、灵活、复杂遍历与多对多性能好、适合 AI/GraphRAG）或 RDF triple store（W3C 语义网标准，适合严格 OWL 形式推理，但设计/变更更重）。
- 关系数据库能承载但不推荐作主存储（关系非原生、需查询时 join 合成，规模膨胀后性能与管理差）。
- Palantir Foundry Ontology 将 Ontology 作为企业架构核心（底层数据库 + 语义层）。
- markdown + frontmatter 的轻量本体（如 frona.ai / obsiko PKM 本体）仅被推荐用于**个人知识管理 / 小规模**场景，不是大规模推荐路径。

当前项目规模：知识库为百级 md 文件，且 PDCA 工作流强依赖"文档即知识、可审阅、可版本化（git diff）"的纯文本特性。

## 决策

**当前采用 markdown 承载本体**：`ontology/<type>/<slug>.md` 节点 + `pdca.asset/v1` frontmatter（id/type/layer/attributes/relations）+ `ontology-validate.py` 门禁校验。

**同时保留升级到图数据库的路径**：不锁死存储，当触发条件满足时可平滑迁移至 Neo4j property graph（或 RDF triple store），且不丢失语义信息。

理由：
- 当前规模下 md 方案零额外依赖、与 git 文档流天然契合、可被人类与 LLM 直接审阅，性价比最高。
- 网络推荐的生产级路径（图数据库）对当前规模是过度工程；但未来规模/推理需求上升时必须可升级，故在架构上预留中性接口。

## 保留升级性的设计保证（已落地）

为使未来迁移不返工，当前 frontmatter 刻意采用**图中立模型**：

- **节点**：`id`（全局唯一，形如 `ontology:<type>/<slug>`）可作图节点 key；`type` 可作图 label。
- **边**：`relations` 字段承载 `specializes` / `composed_of` / `configured_by` / `guides` / `relates_to`，引用全部用本体 id，可机械映射为图关系边。
- **属性**：`attributes[]`（name/desc/constraint/testable_signal）可作节点属性。
- **一致性校验可复用**：`ontology-validate.py` 已做图遍历（引用空悬、关系无环、type 词汇、guides 域/程约束），可直接作为"图导入前的一致性门禁"，无需重写。
- **引用格式中立**：关系引用不绑定 markdown 特有语法，仅依赖本体 id，便于导入图库时解析。

机械映射示例：
- Neo4j：`CREATE (n:<type> {id:<id>, ...attributes})` + `MATCH (a),(b) WHERE a.id=<src> AND b.id=<tgt> CREATE (a)-[:GUIDES]->(b)`
- RDF：`<<id>> <relation> <<target>> .`（subject=id, predicate=relation, object=target）

## 升级触发条件（满足任一即启动迁移评估）

1. 节点规模超过阈值（建议 > 1e3 或可维护性下降）或跨多源系统集成需求出现。
2. 需要 OWL 形式推理，或 GraphRAG / AI agent 多跳推理对遍历性能的要求超出 md 文本检索能力。
3. md 间关系遍历/一致性校验耗时成为瓶颈。

## 影响

- 当前不引入图数据库依赖；ADR-0030（四层物理归并至 `ontology/`）不变。
- 不锁死：frontmatter 图中立模型确保迁移时语义零丢失。
- 风险：若长期不触发升级而规模已超阈值，md 承载的遍历/推理效率会先成为瓶颈；由上述触发条件兜底。
- 后续任务（T0402 试点、T0403 全量）仍按 md 承载执行，门禁不变。
