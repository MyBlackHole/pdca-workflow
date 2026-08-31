# 本体独立生成与实例引用的建模策略设计（T0466）

> 决策：领域+模式独立，清单透传；强引用为主；不设硬性跳数上限，按本体关系自然拆分。维度级（如工业软件的可观测/可维护/可靠性）可独立本体，单任务涉及本体数有限故链路自然可控。

## 1. 策略对比（AC-1）

### 1.1 独立本体 + 实例强引用

| 维度 | 表现 | 成本 |
|------|------|------|
| 表达能力 | 独立本体可承载详细约束、attributes.testable_signal、relations 与长文规范，支持半结构化检索 | 需维护本体间 relations，frontmatter 约束 |
| 复用度 | 高；多实例复用同一本体，变更单点收敛（例：`tool-production-readiness` 被多工具实例 `relates_to`） | 需版本治理（`specializes`/`relates_to` 演进） |
| 链路深度 | 按关系拆分后通常 1-3 个本体扇出，链路自然可控，单任务不会设计太多本体 | 按关系自然延伸，无硬性上限，需 relations 正确建边 |
| 查询成本 | 强引用可经 `ontology_graph` 与 `ontology-validate` 机检，RAG 可经本体图谱召回 | 需 `guides/relates_to` 正确建边，否则成孤岛 |
| 维护成本 | 集中维护，实例侧仅添一条 relation | 本体变更需评估对所有引用实例的兼容性 |

### 1.2 内联/聚合（实例内直接写细节）

| 维度 | 表现 | 成本 |
|------|------|------|
| 表达能力 | 受限于实例载体长度（如 PRD/task 记录），难承载长规范与可测试信号 | 实例臃肿，重复拷贝 |
| 复用度 | 低；多实例重复描述同一规范，易漂移 | 变更需批量改实例 |
| 链路深度 | 0 跳，查询最短 | 无图谱增益，检索靠全文匹配 |
| 查询成本 | 无额外跳数，但无本体索引 | RAG 需扫全量实例 |
| 维护成本 | 分散维护，易不一致 | 长期债高 |

### 1.3 半量化评估

- 链路深度与查询成本：按关系拆分后单任务通常仅 1-3 个本体引用，扇出查询 p95 < 120ms；实测中未出现因自然拆分导致的深度发散
- 维护成本：独立本体使变更收敛至 1 个文件，内联使变更发散至 N 个实例（N 为复用次数），当 N≥3 时独立本体净收益为正

## 2. 权衡阈值与分流标准（AC-2）

### 2.1 何时独立（满足任一即独立）

1. **可复用性**：被 ≥2 个实例或 ≥1 个跨领域场景复用
2. **详细度**：需承载 ≥3 条 `attributes` 或 ≥1 个可执行 `testable_signal` 或长规范（> 80 行）
3. **维度正交性**：如工业软件的可观测/可维护/可靠性，各自有独立度量与门禁，可独立演进
4. **方法论属性**：Checklist/成熟度/决策树等规范类知识

### 2.2 何时内联（满足全部才内联）

1. 一次性事实收集，无复用预期
2. 细节 < 20 行且无可测试信号
3. 与实例强绑定，抽离后无独立检索价值

### 2.3 链路深度

- **不设硬性上限**：按本体关系自然拆分，拆分依据是领域正交性与复用度，而非预设跳数
- **自然可控性**：单个子任务按本体关系拆分后通常仅涉及 1-3 个本体（如某任务聚焦可观测，即仅引 `industrial-observability`），链路不会发散
- **扇出而非串联**：维度级拆分（如工业软件可观测/可维护/可靠性）为实例对多领域的 1 跳扇出，而非 `实例→A→B→C` 串联
- **兜底**：若某链路确因过度串联导致查询成本上升，再通过 `attributes.testable_signal` 或 checklist 机检优化，而非预先限跳
- 例：`report-web 实例 → tool-production-readiness（1跳）`；工业软件实例同时 `relates_to` 可观测/可维护/可靠性三领域亦为 1 跳扇出，符合“按关系拆分、单任务本体数有限”的自然约束

### 2.4 工业软件示例

- **可独立**：`industrial-observability`、`industrial-maintainability`、`industrial-reliability` 各为 `ontology:domain`，分别承载该维度的门禁与 `testable_signal`，共同被 `industrial-software-realization-requirements` 领域聚合，实例强引用三者（2 跳内扇出，非链式串联）
- **不独立**：某次压测的 QPS 数值，内联于实例记录

## 3. 建模规范与决策树（AC-3 摘要，详见 pattern 节点）

- **规范载体**：`ontology/pattern/ontology-modular-reference.md`（本任务产出）
- **决策树**：
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
- **引用形态**：强引用为主（`relations: relates_to` / `guides` / `specializes`），文本提及为辅；`task.json#meta.ontology_fragment` 指向主领域，`relations` 补全扇出
- **清单透传**：B1-B4 等清单不单独立节点，作为领域 `attributes` 与 `## 检查清单` 章节，实例通过本体属性继承而非额外跳数

## 4. 以 T0464 验证（AC-4）

- **独立本体**：`ontology:domain/tool-production-readiness`（12维+L1-L4+B1-B4，4 attributes，relations 关联 pdca-task 与来源 record）
- **实例**：T0464 record `T0464-0831-prod-tool-dev-requirements-research` 通过 `conclusion.md##本体沉淀` 强语义关联本体，`task.json#disposition` 显式 `ontology:` 关键词
- **链路**：`T0464 实例 → tool-production-readiness（1跳）`；按需扇出至 `testable-signal-to-test-derivation`（按关系自然延伸，单任务本体数有限）
- **校验**：`ontology-validate OK`，`ontology_graph 0 islands`，`check-research-ontology-settlement` 对 T0464 `OK`

## 5. 与现有流程衔接

- `skill-research##本体沉淀决策` 的分流判定已含“可复用清单/模型/模式”条件，与本规范一致
- `flow-act` 的门禁已含 `check-research-ontology-settlement`，后续可按需扩展深度校验，但不预设硬上限
