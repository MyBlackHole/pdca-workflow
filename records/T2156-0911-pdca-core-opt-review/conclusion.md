---
schema: pdca.conclusion/v1
id: T2156-0911-pdca-core-opt-review
phase: check
source_ids: [ev2156-core-review-v2, convergence-map-v2]
---

## 上下文

本任务复核 `ontology:concept/pdca` 的设计核心“本体树驱动（B→A→C）”，重点判断 A/B/C 是否应成为核心场景，以及六个 `scenario_type` 是否应下沉为 skill/tool 选择。

## 假设与结果

- 假设 1：A/B/C 表达本体生命周期职责，适合作为核心场景。结果：成立。
- 假设 2：六个 `scenario_type` 更适合作为执行技能与门禁分支，而非核心场景。结果：成立。
- 假设 3：A/B/C 名称可以保持短标签，但需要统一为稳定的语义名。结果：成立。

## AC 对照

- **AC-1** ✅ 推荐核心场景收敛为 A/B/C；六值下沉为 skill/tool 路由，证据：`ev2156-core-review-v2`。
- **AC-2** ✅ 对比了保留六场景、核心 A/B/C + skill 子类型、A/B/C 重命名三类方案，证据：`ev2156-core-review-v2`。
- **AC-3** ✅ 明确后续 Improvement Task 边界：task schema、flow-do、transition gate、skill/tool 选择与 fixture；明确不保留旧六场景兼容层，证据：`ev2156-core-review-v2`。
- **AC-4** ✅ 研究报告可追溯到本体、流程、schema、脚本及 W3C 一手规范，且通过 research web evidence 门禁，证据：`ev2156-core-review-v2`。

## 结论

推荐采用“核心 A/B/C + skill 子类型”双层模型。保留当前 B→A→C 顺序和 A/B/C 短标签；规范名称调整为：B“本体建模”、A“本体实现”、C“本体验证”。六个旧 `scenario_type` 不保留兼容读取，后续迁移任务应一次性改写 schema、门禁、路由和数据。

## 适用边界

本结论是架构研究与立项建议，不直接修改 `ontology/concept/pdca.md`、`ontology/process/flow-do.md` 或任务 schema。结构迁移应另立 Improvement Task，并覆盖一次性数据迁移、门禁拆分和回归 fixture；不新增兼容读取分支。

## 本体沉淀

决策：`ontology:pattern/pdca-core-scene-layering`。

理由：研究结论形成了可复用的场景分层模式，已沉淀为新 pattern；不直接修改既有权威流程正文。后续 Improvement Task 负责把该模式投射到 schema、门禁和路由实现。

## 证据索引

- `ev2156-core-review-v2`：修订后的研究报告，覆盖 AC-1 至 AC-4。
- `convergence-map-v2`：收敛条件与证据映射。

**verdict**: confirmed
- outcome: confirmed
- reason: 用户确认核心只保留 A/B/C，六个 scenario_type 不保留兼容层
- verdict_id: v2156-confirmed
- at: 2026-09-11T10:40:10+08:00
