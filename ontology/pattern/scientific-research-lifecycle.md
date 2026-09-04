---
schema: pdca.asset/v1
id: ontology:pattern/scientific-research-lifecycle
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/scientific-research-lifecycle/1.0.0
summary: 科学调研I2S2生命周期支：proposal→peer-review→experiment→processing→publish + 绿色保育（对齐OAIS）
relations:
  specializes:
  - ontology:pattern
  guides:
  - ontology:concept/domain-entity
  relates_to:
  - ontology:pattern/research-diagram-methodology
  - ontology:concept/knowledge-provenance
attributes:
- name: lifecycle_phases
  desc: 4阶段+绿色保育
  constraint: 准备→采集→计算→发表，发表驱动新研究，绿色保育（编目/存档/保存/I PR）
  testable_signal: 运行 grep -q 'lifecycle' ontology/pattern/scientific-research-lifecycle.md
    && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q
    'OK'
- name: representation_information
  desc: 表示信息
  constraint: 需 `Representation Information`（规范/字典/工具）才能渲染理解数据
  testable_signal: 检查本文件含 'OAIS' 且经 validate 通过 且运行 grep -q 'fix' ontology/pattern/scientific-research-lifecycle.md
    && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q
    'OK'
- name: experimental_workflow_shape
  desc: 实验工作流形
  constraint: 线性（单流水）或分支（对照臂平行），1读向，时间同高，Sample n 必显
  testable_signal: 检查本文件含 'workflow' 且经 validate 通过 且运行 grep -q 'fix' ontology/pattern/scientific-research-lifecycle.md
    && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q
    'OK'
---

# 科学调研I2S2生命周期支

> 来源 `Bath I2S2 Idealised Research Activity Lifecycle` + `OAIS` + `sci-draw workflow`

- **4阶段**：`study preparation→data collection→computational→publication` 循环，`ENCORE` 聚 `stage3` 可重复，发表驱动新研究
- **绿色保育**：`appraisal→documentation(metadata/provenance)→storage/archive/preservation→IPR` 经 `OAIS Representation Information` 保长期可理解
- **工作流图**：线性（采集→处理→分析→输出）或分支（处理vs对照臂等高），`Sample n` 必显，`time` 单向
