# T0402 验收标准覆盖补充（非 map 证据）

本证据覆盖 PRD 中未被 migration-manifest / validate-pass 直接登记的 AC，供 Check 门禁的
ACCEPTANCE_CRITERION_UNCOVERED 检查使用（非 convergence-map 类型）。

- **AC-3** 每 KnowledgeArtifact 实例含结构化 attributes（applicability + testable_signal）：
  见 `ev-t0402-validate-pass`，`ontology-validate.py` 的 AC-4 校验 `attributes[].testable_signal`
  存在且非空，全部 16 个知识实例通过。
- **AC-4** 每实例至少 1 条 `guides` 指向领域/过程类（或 `relates_to`）：
  见 `ev-t0402-validate-pass`，`ontology-validate.py` 的 AC-5 校验
  `type∈KNOWLEDGE_VOCAB` 的节点须含 `guides`/`relates_to`，全部通过（含 fact 实例已补 guides）。
- **AC-7** `records/*/evidence/` 下的 tls 代码/日志未迁移，仅 `knowledge/` 文本迁移且原位置保留 redirect：
  见 `ev-t0402-migration-manifest` 节点清单，仅含 `ontology/` 新增节点与 `knowledge/` 的
  redirect 桩，无任何 `records/` 路径被改写，符合「保留不可变记录」的范围边界。
