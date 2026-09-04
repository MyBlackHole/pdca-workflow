---
schema: pdca.asset/v1
id: ontology:domain/skill-context-retrieval
name: context-retrieval
summary: Retrieve relevant context from knowledge assets for task execution.
description: 按任务场景、阶段、标签和来源链选择最小可信 AI 上下文
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-context-retrieval/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


---
schema: pdca.asset/v1
id: skill:context-retrieval
layer: skill
name: context-retrieval
description: 按任务场景、阶段、标签和来源链选择最小可信 AI 上下文
summary: 从结构化四层资产中检索并组装当前任务的最小可信上下文
tags: [context-retrieval, provenance]
scenarios: [default]
phases: [plan, do, check, act]
applies_when: [开始任务或阶段切换后需要加载历史上下文]
excludes_when: [用户明确要求不读取历史资料]
source_ids: [knowledge:information-architecture.four-layer-context-model, knowledge:information-architecture.task-fingerprint-reranking]
confidence: high
status: active
---
# 精准上下文检索

## 输入

- 当前任务的目标、scenario、PDCA phase、约束和关键实体。

## 执行步骤

1. 将问题压缩成少量普通文本关键词，并提取明确的标签和适用/排除信号。
2. 读取 doctor 的 `context.retrieve` 能力结果。可用时通过当前环境 Adapter 执行推荐；不可用时用 `rg` 在 `ontology/domain/`、`records/` 和任务元数据中搜索相同关键词，并按 applies/excludes/source_ids 手工筛选最小集合。

3. 检查 fingerprint、总分、评分组成、排除原因和 source IDs，只加载真正影响当前决策的资产。
4. 需要解释、反例或冲突消解时，加 `--expand-experience`；默认不展开 Experience，永不推荐 Evidence。
5. 需要核验事实时，再沿 Experience source ID 查看 Evidence 摘要；除非必要，不读取 blob。
6. 将采用的上下文及理由追加到任务 `implement.jsonl`。Adapter 提供回执能力时记录 used/helpful/misleading；filesystem fallback 只记录文件、理由和 source IDs，不伪造回执 ID。

7. 反馈在 `task learn` 时随 Context 记录封存；只有已闭环记录中的反馈会影响相似任务。

## 输出

- 最小上下文文件列表。
- 每项资产与当前任务的匹配理由。
- 推荐回执 ID，供反馈绑定资产内容版本。
- 若追溯来源，记录展开到的最深层级。

## 失败处理

- 推荐无结果：检查 query/tag/signal 是否过窄，再显式放宽；不要直接加载全部 records。
- `context.retrieve` 不可用：执行 filesystem-search fallback；fallback 也失败时停止并报告缺失能力。
- 来源缺失、digest 漂移或层级方向错误：停止使用该资产并报告验证失败。
- Knowledge 相互冲突：展开各自 Experience 和 Evidence，再由当前任务验收标准裁决。
- 资产内容在推荐后变化：废弃旧回执并重新执行 recommend，不迁移旧版本反馈。

## 已知坑

- 按任务场景/阶段/标签选最小可信资产，勿全量加载历史记录凑上下文。
