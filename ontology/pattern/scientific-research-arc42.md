---
schema: pdca.asset/v1
id: ontology:pattern/scientific-research-arc42
type: pattern
layer: Knowledge
status: active
summary: 科学调研arc42支：12节全架构文档模板（对齐arc42.org）
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: twelve_sections
    desc: 12节
    constraint: 1目标2约束3上下文4方案5构件（C4）6运行时7部署8概念9决策10质量11风险12词汇
    testable_signal: "检查本文件含 'arc42' 与 '12节' 且经 validate 通过"
  - name: c4_integration
    desc: C4集成
    constraint: arc42 5构件视图即C4，6运行时即时序
    testable_signal: "检查本文件含 'C4' 且经 validate 通过"
---

# 科学调研arc42支

> 来源 `arc42.org` 12节模板（德起源，欧广用）

- **12节**：1目标2约束3上下文4方案5构件(C4)6运行时(时序)7部署8概念9决策(ADR)10质量11风险12词汇 — `arc42` 重于多需，节清单即严肃架构文档自检表
- **与C4组合**：`arc42 5` 即 `C4`，`arc42 6` 即时序，互补不替
