# SSOT v3 演进记录（T0399 设计落地一致性处置）

## 背景
- T0400（0829-onto-ssot-schema）已归档，其产物 `ontology/README.md`（taxonomy 式 v1）、`schemas/ontology-asset.schema.json`、`scripts/ontology-validate.py`、`skills/ontology-check/SKILL.md` 基于"知识形态（pattern/principle…）作 `type` 顶层分类"的 **taxonomy（分类法）** 模型。
- 经 6 轮 grill + 用户纠偏（"本体呢"指向我们停留在分类法）+ 网络资料（Gruber 五原则、Stanford Ontology 101、Palantir "Model reality not systems"、Schema-vs-Ontology 区分、MDPI 属性/关系丰富度）自我审查，确认原模型是分类法而非本体。
- v2/v3 草案逐步修正为**实体本体模型**：实体类型层次（specializes is-a）+ 结构化属性（可派生测试）+ 关系图（guides/composed_of/configured_by/relates_to）；知识形态作 `KnowledgeArtifact` 子类经 `guides` 挂接领域实体；目录平铺仅索引。

## v3 模型要点（详见活跃 `ontology/README.md`）
- 类型受控词汇：`domain`/`entity`/`concept`/`process`/`role`/`pattern`/`principle`/`pitfall`/`fact`/`decision`。
- 实体类型层次：`Entity` → `DomainEntity`(TLSSession/MTLSHandshake/X509Certificate/TLSConfiguration/TLSTestHarness/ExecStdinPump) / `Process`(CodeReviewProcess) / `KnowledgeArtifact`(Pattern/Principle/Pitfall/Fact/Decision)。
- 关系带 domain/range；`guides` 是知识挂接实体的核心；每 KnowledgeArtifact 实例至少 1 条 `guides`/`relates_to`。
- 属性结构化（applicability/constraints/testable_signal），防 taxonomy 退化。
- 校验器 AC1–AC6（含 type 词汇、引用非空悬、无环、属性测试覆盖、关系丰富度、guides 域/程约束）。

## 一致性处置
- **活跃基础设施已按 v3 修订**：`ontology/README.md`、`schemas/ontology-asset.schema.json`、`scripts/ontology-validate.py`、`skills/ontology-check/SKILL.md`。
- **T0400/T0401 归档产物保持不可变**（PDCA 不可变记录原则）；本记录与活跃 SSOT README 顶部注记共同说明"v3 取代 v1"，不在归档产物内改写。
- 后续 T0402（tls 试点）、T0403（全量迁移）按 v3 实体树执行迁移与 `ontology-validate.py` 校验。

## 确认记录
- T0399 `clarifications.jsonl` 已登记 `direction_confirm`：SSOT v3 实体本体模型确认（2026-08-29T18:52:23+08:00）。
- T0399 `final_confirmation`（design 阶段）已于 2026-08-29T18:03:40+08:00 落盘，覆盖"完整本体三合一语义引擎"方向；v3 为其模型细化，按门禁不重复写 `final_confirmation`。
