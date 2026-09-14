---
schema: pdca.asset/v2
id: ontology:concept/pdca-execution-contract
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: CONTRACT-01：复用任务／计划／验收，不造平行大对象
---

# CONTRACT-01：复用任务／计划／验收，不造平行大对象

Plan前把用户问题、目标、范围、非目标、预期产物写在任务说明和phase_start请求。获准Plan后产出计划、固定输入、验收标准及测试设计；用户启动Do时共同固定其版本与写域。不另建GoalContract／PhaseContract体系。

任务计划至少明确：work_product、required_actions、constraints、testable_signal。具体AC说明可检验的预期和失败边界；Claim—Evidence—Verdict解释如何满足AC，不能取代AC或事后改expected。

固定输入清单列真实ref、sha256、角色（需求／本体／实现／工具／参考）和保存方式；摘要固定内容，不证明真实执行或来源。冻结oracle改变需要新Plan及新attempt；不得因测试失败放宽。

各场景的必需产物由SCENE与已批准目标共同确定。知识地图只有满足稳定对象身份、关系、约束、来源和可检验性才可作为本体，不因叫ontology_modeling而自动合格。

记录格式在[记录契约索引](../contracts/record-shapes/index.md)，仅采用其中列出的 v4 schema 与示例。旧字段索引／生成规则在 legacy，不从旧格式抄入默认 PASS 或两次确认语义。
