---
schema: pdca.asset/v1
id: ontology:entity/TEMPLATE-SYSTEM
type: entity
layer: Knowledge
status: active
summary: 【填】全栈系统聚合（composed_of X叶，C4 L2/L3 至 核心pipeline 可建模）
relations:
  specializes:
    - ontology:concept/domain-entity
  composed_of:
    - ontology:entity/TEMPLATE-LEAF-1
    - ontology:entity/TEMPLATE-LEAF-2
    - ontology:entity/TEMPLATE-LEAF-3
  relates_to:
    - ontology:pattern/production-ontology-scientific-gate
    - ontology:pattern/scientific-research-methodology
attributes:
  - name: c4_l2_coverage
    desc: C4 L2 全栈容器覆盖
    constraint: 覆盖 【填】→【填】→【填】 横切 【填】的容器图且 mermaid 可渲染
    testable_signal: "运行 grep -q 'C4 L2' records/<record>/research-report.md 且 grep -c '```mermaid' records/<record>/research-report.md | awk '{exit !($1>=3)}'"
  - name: pipeline_depth
    desc: 核心 pipeline 下钻至 L3 可测
    constraint: 下钻至 【填】 stage 位图与 pipeline 宏，含 【填】分支
    testable_signal: "运行 grep -q 'PIPELINE' records/<record>/research-report.md 且 grep -q 'STAGE_' /tmp/zfs/include/sys/<file>.h 命中"
  - name: leaf_completeness
    desc: 叶 composed_of 完整性与 100% Rule
    constraint: composed_of 恰为 【填】叶且可 scaffold 且覆盖率≥95%（以 module 下文件为参照）
    testable_signal: "运行 python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/TEMPLATE-SYSTEM 检查 PASS 且 python3 scripts/ontology_graph.py --format summary | grep -q 'islands: 0'"
---

# 【填】全栈系统（System）

系统聚合：`composed_of` 【填】叶（`【填】`），以 `research-diagram-methodology` 多图 `mermaid` 为可视化证据（C4 L2 全栈 + 核心 pipeline 时序 + 聚合决策树），每图附 `Source: file:line` 直达 `openzfs/zfs#master`。

验证：`grep -c '```mermaid' records/<record>/research-report.md` ≥3 且 `python3 scripts/ontology-validate.py` 0 issue 且 `islands:0`。

Source: `records/<record>/research-report.md` + `openzfs/zfs/include/sys/<file>.h`

## C4 L2 全栈 — 【填】横切

系统 L2 容器图：【填】叶如何横切，`C4 L2` 图以 `【填】 → 【填】 → 【填】` 呈现。

```mermaid
graph TD
    User --> ZPL
    ZPL --> DMU --> DSL --> SPA --> ZIO --> VDEV
    SPA -.-> ARC
    %% Source: openzfs/zfs/include/sys/spa_impl.h:80
```

Source: `openzfs/zfs/include/sys/spa_impl.h:80` + `openzfs/zfs/include/sys/zio_impl.h:60`

## 时序 — 【填】端到端

【填】端到端五步：`【填】 → 【填】 → 【填】 → 【填】 → 【填】`，时序图覆盖 `【填】 → pipeline → VDEV` 全链。

```mermaid
sequenceDiagram
    participant App as App
    participant Sys as System
    participant Leaf as Leaf
    App->>Sys: write()
    Sys->>Leaf: dispatch
    Leaf-->>Sys: done
    %% Source: openzfs/zfs/module/zfs/spa.c:2400
```

Source: `openzfs/zfs/module/zfs/spa.c:2400`

## 决策树 — 聚合维度选型

本系统聚合决策：当新需求到达时，按 100% Rule 判定维度归属。

```mermaid
flowchart TD
    START([新需求/新模块]) --> Q1{属于哪一叶维度?}
    Q1 -- 已有叶维度 --> A1[归入既有叶，补属性与时序]
    Q1 -- 新维度且正交 --> Q2{是否满足三准绳?}
    Q2 -- 是 --> A2[新建 leaf，加入 system composed_of]
    Q2 -- 否 过细 --> A3[合并至近邻叶 via relates_to]
    Q2 -- 否 过粗 --> A4[split 为两叶]
    A1 --> Q3{100% 覆盖率≥95%?}
    A2 --> Q3
    Q3 -- 否 --> A5[补缺口叶]
    Q3 -- 是 --> END([gate --check hundred PASS])
    %% Source: ontology/domain/ontology-hybrid-methodology.md:47 三准绳
```

Source: `ontology/domain/ontology-hybrid-methodology.md:47` + `ontology/pattern/production-ontology-scientific-gate.md`

## 正例

```markdown
# 正例：按三件套新增一叶并保持 100% Rule
cp templates/production-entity.md ontology/entity/new-leaf.md
# 三属性 + 八段 + Source
python3 scripts/production-ontology-gate.py --node ontology:entity/new-leaf  # PASS
# 更新 system composed_of 加入 new-leaf
python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/TEMPLATE-SYSTEM  # PASS 覆盖率≥95%
```

## 反例

```markdown
# 反例：直接在 system 内堆砌新维度描述，不建 leaf
# 错：system.md 内新增 200行 VDEV 描述，但 composed_of 仍 6叶，gate --check hundred -> FAIL 缺维度
# 正确：新建 entity/zfs-vdev.md 并加入 composed_of
```

## 门禁

- **多图门禁**：`grep -c '```mermaid' records/<record>/research-report.md` ≥3
- **溯源门禁**：`grep -c 'Source:' records/<record>/research-report.md` ≥3
- **正文门禁**：`wc -l ontology/entity/TEMPLATE-SYSTEM.md` ≥60 且 `grep -q '决策树' && grep -q '正例' && grep -q '反例'`
- **属性门禁**：`attributes` ≥3 且每条 `testable_signal` 含 `gate.py` 或 `grep -q`
- **100% 门禁**：`python3 scripts/production-ontology-gate.py --check hundred --node ontology:entity/TEMPLATE-SYSTEM` PASS
- **本体校验**：`python3 scripts/ontology-validate.py` 0 issues 且 `islands:0`
- **Gate 门禁**：`python3 scripts/production-ontology-gate.py --all` GATE OK
