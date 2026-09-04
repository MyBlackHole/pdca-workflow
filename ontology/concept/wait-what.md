---
schema: pdca.asset/v1
id: ontology:concept/wait-what
name: Wait-What
summary: 上下文缺失时重新 pitch：用 CONTEXT.md 词汇重新表述
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/wait-what/1.0.0
relations:
  specializes:
    - ontology:concept/domain-modeling
---

# Wait-What

当 agent 的输出没有命中预期时，触发重新 pitch 机制——用 CONTEXT.md 的共享语言重新表述需求，而非猜测。

## 触发条件

- agent 的响应与预期不符
- 上下文信息不足以做出正确判断
- 术语或概念存在歧义
- 共享语言缺失或不一致

## 机制

1. **停止猜测**：不假设、不脑补，直接指出上下文缺失
2. **重新 pitch**：用 CONTEXT.md 的共享语言重新表述需求
3. **精确化**：提出精确的规范术语（`sharpen-language`）
4. **挑战术语表**：当用户使用与现有术语冲突的词时立即指出（`challenge-glossary`）

## 与相关概念的关系

- `challenge-glossary`：当用户使用冲突术语时立即指出
- `sharpen-language`：模糊语言精确化
- `domain-modeling`：构建共享语言
- `writing-for-agents`：为 agent 写作

## AI 效率机制

- 防止 agent 在上下文缺失时编造答案
- 用共享语言消除歧义
- 减少因误解导致的返工

## 边界

`wait-what` 是触发机制，不是自动检查；它约束提问方式而非替代人工判断。

