---
schema: pdca.asset/v1
id: ontology:concept/pdca-execution-contract
type: concept
layer: Knowledge
summary: 由本体产出驱动执行内容的结构化契约
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
dcterms_modified: 2026-09-11
owl_versionIRI: http://pdca.local/ontology/pdca-execution-contract/1.0.1
relations:
  specializes:
    - ontology:concept/entity
  relates_to:
    - ontology:concept/pdca-task
    - ontology:concept/pdca-evidence
attributes:
  - name: contract_fields
    desc: 执行契约的最小结构
    constraint: 必须声明 work_product、required_actions、constraints 和 testable_signal
    testable_signal: "grep -q 'work_product' schemas/task.schema.json && grep -q 'required_actions' schemas/task.schema.json"
  - name: contract_authority
    desc: 本体产出契约是 Do 执行内容的唯一业务来源
    constraint: skill/tool 只能作为执行适配器，不得新增未声明的业务动作
    testable_signal: "grep -q 'execution_contract' ontology/process/flow-do.md && grep -q '执行适配器' ontology/process/flow-do.md"
---
# PDCA 执行契约

`execution_contract` 是本体建模结果到 AI 执行器之间的唯一业务接口。它声明要产出什么、必须执行哪些动作、需要遵守哪些约束，以及如何验证完成。

工具和 skill 不定义任务类别，也不决定业务范围；它们只负责把契约动作映射为具体执行协议。
