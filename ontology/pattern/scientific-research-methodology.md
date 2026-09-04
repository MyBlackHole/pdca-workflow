---
schema: pdca.asset/v1
id: ontology:pattern/scientific-research-methodology
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/scientific-research-methodology/1.0.0
summary: 科学调研方法论根：C4+Diátaxis+arc42+I2S2生命周期四支（对齐c4model/diataxis/arc42/Bath I2S2）
relations:
  specializes:
    - ontology:pattern
  relates_to:
    - ontology:pattern/scientific-research-c4
    - ontology:pattern/scientific-research-diataxis
    - ontology:pattern/scientific-research-arc42
    - ontology:pattern/scientific-research-lifecycle
  relates_to:
    - ontology:pattern/research-diagram-methodology
    - ontology:concept/knowledge-provenance
    - ontology:pattern/ontology-modular-reference
attributes:
  - name: four_pillars
    desc: 四支
    constraint: C4架构可视 + Diátaxis文档四象限 + arc42 12节 + I2S2生命周期，可图可表
    testable_signal: "运行 python3 scripts/ontology_graph.py --format summary 检查本根 composed_of 4叶可追且 islands:0，且 grep -R 'C4' ontology/pattern/scientific-research-*.md 可命中"
  - name: research_diagram_integration
    desc: 多图集成
    constraint: C4 L2 + Diátaxis reference + arc42 5/6 + I2S2 workflow 皆 mermaid inline，每图1 Source
    testable_signal: "运行 grep -c 'mermaid' ontology/pattern/research-diagram-methodology.md 检查≥3 且经 validate 通过"
---

# 科学调研方法论根（C4+Diátaxis+arc42+I2S2）

> 综合 `c4model.com` + `diataxis.fr` + `arc42.org` + `Bath I2S2 OAIS` + `sci-draw workflow`，为 `research` 提供架构师可一图建模的科学背书

## 四支

- **C4**：4层级+4补充图，边缘交叉靶 0/<3/<5
- **Diátaxis**：`tutorial/how-to/reference/explanation` 四且仅四，罗盘纠混
- **arc42**：12节全架构文档，`5`即C4，`6`即时序
- **I2S2**：`proposal→peer-review→experiment→processing→publish` + 绿色保育 + 工作流线性/分支形

## 与多图模板

`research-diagram-methodology` 6图即 `C4 L2` + `Diátaxis reference` + `arc42 5/6` + `I2S2 workflow` 的 `mermaid` 实现，每图 `Source: primary` 溯源。

## 应用

`T0501` 类ZFS Crypto研究可直接 `specializes` 该根，6图外加 `arc42:10` 质量与 `I2S2` 生命周期可追溯。
