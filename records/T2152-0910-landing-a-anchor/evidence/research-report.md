# T2152 research-report：收紧默认锚定方案

## 调研目标

设计 `task_identity` 默认锚定收紧方案：新节点按领域挂分支，
不再默认全挂 `pdca-task`；存量只清点不批量改。

## 方法

代码取证默认锚定逻辑 + 子树分布统计 + 增量/存量分流设计。

## 发现

### 架构图 C4 L2（mermaid）

```mermaid
graph TB
    TI[task_identity create<br/>PDCA_TASK_NODE默认]
    PT[ontology:concept/pdca-task]
    PD[ontology:concept/pdca<br/>303直接引用]
    DOM[domain/* 分支<br/>313节点已在此]
    TI --> PT
    PT --> PD
    DOM -.->|弱挂靠| PD
```

Source: scripts/task_identity.py:44（`PDCA_TASK_NODE` 默认锚定常量）

### 逻辑图 目标锚定流（mermaid）

```mermaid
flowchart TD
    N[新节点] --> Q{领域可判?}
    Q -->|技能| S[domain/pdca分支]
    Q -->|领域知识| D[domain/对应分支]
    Q -->|PDCA机制| P[pdca-task保留]
    Q -->|不明| H[人工指定]
    S & D & P & H --> V[ontology-validate]
```

Source: scripts/task_identity.py:292-315（未显式锚定时继承/默认逻辑）

### 生命周期图 迁移策略（mermaid）

```mermaid
stateDiagram-v2
    [*] --> 增量收紧: 新节点按分支挂
    [*] --> 存量清点: 弱关联清单归档
    存量清点 --> 不批量改: 风险冻结
    增量收紧 --> 单测覆盖
    单测覆盖 --> 门禁全绿
    不批量改 --> 门禁全绿
    门禁全绿 --> [*]
```

Source: https://docs.pytest.org/（单测方法背景）

## 结论与建议

1. 改 `task_identity` 默认策略为领域分支挂靠，保留显式 `--ontology-anchor` 覆盖。
2. 存量 303 直接引用只清点出迁移清单，不批量改（冻结风险）。
3. 新策略单测覆盖创建路径，回归全绿进 Check。

## 术语表

- 默认锚定：未显式指定时自动继承/回落的 ontology 挂接。
- 弱关联：仅 `relates_to` 的挂靠（789 条，近 specializes 两倍）。

## 参考资料

- pytest 单测方法背景：https://docs.pytest.org/
- Git 变更追溯方法背景：https://git-scm.com/doc
- Source: ontology/concept/pdca-task.md（锚定目标节点，可复核）
- Source: https://docs.pytest.org/（单测方法背景）
