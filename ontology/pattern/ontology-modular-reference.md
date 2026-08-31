---
schema: pdca.asset/v1
id: ontology:pattern/ontology-modular-reference
type: pattern
layer: Knowledge
status: active
summary: 本体模块化与实例引用模式：独立本体+强引用，按关系自然拆分，清单透传
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/pdca-task
    - ontology:concept/domain-model
  relates_to:
    - ontology:concept/ontology-asset
    - ontology:concept/ontology-validate
    - ontology:domain/skill-ontology-check
    - ontology:domain/tool-production-readiness
    - ontology:pattern/testable-signal-to-test-derivation
attributes:
  - name: when_to_split
    desc: 何时将知识独立为本体节点
    constraint: 满足任一即独立：被≥2实例或跨领域复用；需≥3条attributes或可执行testable_signal或长规范>80行；维度正交可独立演进（如可观测/可维护/可靠性）；方法论/Checklist/成熟度类
    testable_signal: 对候选知识检查是否满足上述任一条件，满足则应在 ontology/<type>/<slug>.md 新建节点且经 ontology-validate 通过，否则应内联于实例
  - name: link_depth
    desc: 实例到本体的链路深度
    constraint: 不设硬性跳数上限，按本体关系自然拆分；单个子任务按关系拆分后通常仅涉及1-3个本体，链路自然可控；维度级拆分（如可观测/可维护/可靠性）为扇出而非串联
    testable_signal: 检查实例的强引用本体均存在且为 pdca.asset/v1，且经 python3 scripts/ontology_graph.py 检查无孤岛；单任务引用本体数通常≤3，否则复核拆分合理性
  - name: reference_form
    desc: 实例对独立本体的引用形态
    constraint: "强引用为主（relations 显式边 relates_to/guides/specializes），文本提及为辅；task.json#meta.ontology_fragment 指向主领域，relations 补全扇出"
    testable_signal: 检查实例（task.json或record）的 relations 含至少一条指向独立本体的显式边，且该本体存在且为 pdca.asset/v1，否则视为弱引用不合规
  - name: checklist_propagation
    desc: 清单类知识的透传而非独立节点
    constraint: B1-B4等清单不单独立节点，作为领域节点的attributes与##检查清单章节，实例通过本体属性继承而非额外跳数
    testable_signal: 对清单类本体检查其不存在独立的 ontology/pattern/<checklist>.md，而是在领域节点的 attributes 中承载且可被 grep "## 检查清单" 命中
---

# 本体模块化与实例引用模式

> 决策：领域+模式独立，清单透传；强引用为主；不设硬性跳数上限，按本体关系自然拆分。维度级（如工业软件的可观测/可维护/可靠性）可独立本体，单任务本体数有限故链路自然可控。

## 决策树

```
是否满足“独立”任一条件？ ──否──→ 内联（实例内描述，records-only 可）
                         │
                         是
                         ▼
                    是否已存在可复用领域/模式？ ──是──→ 强引用（relations: relates_to/guides）
                         │
                         否
                         ▼
                    新建领域/模式节点（attributes + testable_signal + relations）
                         │
                         ▼
                    按本体关系建边（扇出多维度而非串联），经 ontology-validate + ontology_graph（0 islands） + check-research-ontology-settlement 校验
                    单任务仅涉及 1-3 个本体，链路自然可控，无硬性跳数上限
```

## 分流标准

### 独立（满足任一）

1. 被 ≥2 实例或跨领域复用
2. 需 ≥3 attributes 或可执行 testable_signal 或长规范 >80 行
3. 维度正交可独立演进（如工业软件：`industrial-observability` / `industrial-maintainability` / `industrial-reliability`）
4. 方法论/Checklist/成熟度/决策树类

### 内联（满足全部）

1. 一次性事实收集，无复用预期
2. 细节 <20 行且无 testable_signal
3. 与实例强绑定，抽离后无独立检索价值

## 链路深度

- 不设硬性上限：按本体关系自然拆分，拆分依据是领域正交性与复用度
- 自然可控性：单个子任务按本体关系拆分后通常仅涉及 1-3 个本体，链路不会发散
- 扇出而非串联：维度级拆分（如工业软件可观测/可维护/可靠性）为实例对多领域的 1 跳扇出，而非串联
- 校验：`ontology_graph` 0 islands 且强引用本体均存在且可达，单任务本体数通常 ≤3

## 引用形态

- 强引用：`relations: relates_to` / `guides` / `specializes` 显式边，可被 `ontology-validate` 与图谱校验
- 文本提及：仅补充说明，不作为机检依据
- 实例侧：`task.json#meta.ontology_fragment` 指向主领域，`relations` 补全扇出

## 清单透传

- 清单不单独立节点，作为领域 `attributes` 与 `## 检查清单` 章节
- 实例通过本体属性继承清单，而非 `实例→清单本体` 额外跳数
- 例：`tool-production-readiness` 的 B1-B4 清单在领域节点内，`report-web` 实例引用该领域即继承清单

## 示例

### 工业软件

- 独立：`ontology:domain/industrial-observability`、`industrial-maintainability`、`industrial-reliability` 各承载该维门禁与 testable_signal，被 `industrial-software-realization-requirements` 聚合，实例 1 跳扇出引用三者
- 不独立：某次压测 QPS 数值，内联于实例 record

### T0464 正例

- 领域：`ontology:domain/tool-production-readiness`（12维+L1-L4+B1-B4）
- 实例：`T0464-0831-prod-tool-dev-requirements-research` → 领域 1 跳；按需扇出至 `testable-signal-to-test-derivation`，按关系自然延伸

## 与流程衔接

- `skill-research##本体沉淀决策` 的“可复用清单/模型/模式”分流条件与本模式一致
- `flow-act` 已挂接 `check-research-ontology-settlement`，后续可扩展为 `check-ontology-reference-depth.py`

## 溯源

- 任务：T0466 `pdca/tasks/0831-ontology-instance-reference-modeling/task.json:1`
- 示例：`ontology:domain/tool-production-readiness`
- 讨论：用户提出“工业软件可拆可观测/可维护/可靠性独立本体”，链路过深的顾虑
