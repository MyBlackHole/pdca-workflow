---
schema: pdca.asset/v1
id: ontology:concept/domain-modeling
type: concept
layer: Knowledge
status: active
summary: 领域建模：活跃构建和维护项目领域模型
relations:
  specializes:
  - ontology:principle
---


# Domain Modeling

领域建模：活跃构建和维护项目领域模型。

## 单/多上下文判定

- **单上下文**：单一 `CONTEXT.md` 于根，适于小域
- **多上下文**：存在 `CONTEXT-MAP.md` 于根，路由至各 bounded context 的 `CONTEXT.md`（如 `src/ordering/CONTEXT.md`, `src/billing/CONTEXT.md`），`docs/adr/` 分 system-wide 与 context-specific 两层
- **创建惰性**：仅当有术语/决策可写时才创建文件，无 `CONTEXT-MAP.md` 则为单上下文
- **判定**：当跨子域术语冲突或独立演进时启用 MAP，否则保持单文件以控 `context load`

## 与 wizard/多上下文协同

wizard 的 Scope 阶段读 `CONTEXT-MAP.md` 以识别上下文边界；多上下文下 `domain-modeling` 按 MAP 分发术语更新。
