---
schema: pdca.asset/v1
id: ontology:pattern/scientific-research-c4
type: pattern
layer: Knowledge
status: active
summary: 科学调研C4支：4层级+4补充图与边缘交叉靶（对齐c4model.com）
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/domain-entity
  relates_to:
    - ontology:pattern/research-diagram-methodology
attributes:
  - name: four_levels
    desc: C4 4层级
    constraint: L1 Context/L2 Container/L3 Component/L4 Code 每图单层级，不混层
    testable_signal: "检查本文件含 'C4 L1' 与 'C4 L2' 与 'C4 L3' 且经 validate 通过"
  - name: supplementary
    desc: 4补充图
    constraint: dynamic/deployment/landscape/decision 四补充
    testable_signal: "检查本文件含 'dynamic' 与 'deployment' 且经 validate 通过"
  - name: edge_target
    desc: 边缘交叉靶
    constraint: 6元以下0交叉，7-12元<3，>12元<5（Purchase et al.）
    testable_signal: "检查本文件含 'edge' 与 '交叉' 且经 validate 通过，且 graph islands:0"
---

# 科学调研C4支

> 来源 `c4model.com` Brown + `arc-kit C4-layout` Purchase/Sugiyama

- **4层级**：`L1 Context`（系统边界最大视觉）→ `L2 Container`（可部署单元）→ `L3 Component`（模块）→ `L4 Code`（按需）每图单层级 `C4-PlantUML` 或 `Mermaid C4Context`
- **4补充**：`dynamic`（时序式）、`deployment`（`subgraph` 嵌套VPC）、`landscape`、`decision`
- **质量门**：`edge crossings 0/<3/<5`、`visual hierarchy` 系统边界最突出、`grouping` 临近、`flow` 单向、`traceability` 可跟、`abstraction` 单层
