---
schema: pdca.asset/v1
id: ontology:concept/to-spec
name: To Spec
summary: 将对话转化为规格说明：grilling 输出的结构化捕获
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/to-spec/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
---

# To Spec

将 grilling 会话的输出转化为正式规格说明（spec），作为后续实现的依据。

## 核心做法

1. **捕获 grilling 输出**：将 grill-with-docs 或 grilling 会话的决策树、前沿、共识转化为结构化 spec
2. **声明式格式**：spec 是机器可读的声明，不是自由文本
3. **可追溯**：spec 引用 grilling 会话的证据（clarifications.jsonl 条目）
4. **可验证**：spec 的每个条目可以被后续实现和测试验证

## Spec 结构

- **目标**：要实现什么
- **约束**：不可违反的条件
- **接口**：模块/接口/seam/adapter/depth 定义
- **验收标准**：如何验证 spec 是否被正确实现
- **证据**：链接到 grilling 会话记录

## 与相关概念的关系

- `grilling`：追问方法论，产生 spec 的输入
- `grill-with-docs`：结合 grilling + domain-modeling + spec
- `implement`：从 spec 构建实现
- `tracer-bullet`：从 spec 派生的垂直切片
- `design-tree`：spec 的决策树结构

## AI 效率机制

- 捕获 grilling 的输出，避免重复追问
- 为 implement 提供明确的输入
- 使实现可验证、可追溯

## 边界

spec 是 grilling 输出的捕获，不是新创建的文档；spec 的质量取决于 grilling 的深度。

