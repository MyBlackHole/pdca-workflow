---
name: code-comments
description: Use when adding Chinese annotation comments to code, when asked to translate/add supplementary comments in Chinese to existing code, or when needing to embed business-understanding diagrams (ASCII / Mermaid) alongside source code for clearer business logic visualization, or when documenting technical principles / architecture decisions / algorithm mechanisms / system architecture understanding inline for deeper code comprehension
---

# Adding Chinese Code Comments (代码备注)

## Core Rules

1. Add Chinese `// 备注:` blocks BEFORE functions/classes/key segments
2. PRESERVE all original English comments — NEVER remove/modify/merge
3. Chinese is supplementary, on separate adjacent lines, never replacing English
4. EDIT THE ORIGINAL FILE IN-PLACE — no separate annotation files
5. Do NOT change any code — comments-only edits
6. Unified prefix: `// 备注:` — consistent across codebase
7. Skip trivial one-liners (`count++`), obvious getter/setter, boilerplate

## Formats

**Function/Class block:**
```
// 备注：处理用户数据，验证邮箱，计算活跃度得分
// original English comment — DO NOT TOUCH
func existingFunction() {
```

**Code segment line:**
```
// 备注：验证用户输入合法性
// original English comment — DO NOT TOUCH
const result = someOperation();
```

## Business Understanding Diagrams

Add inline diagrams (ASCII or Mermaid) for non-trivial business flows (3+ steps). Each diagram answers ONE business question, max 20 lines, with Chinese labels and a legend.

**Prefer ASCII box-drawing** over Mermaid for simple flows. Use Mermaid only when state/sequence complexity demands it.

## Principle Comments

Add BEFORE non-obvious code mechanisms. **Explain WHY, not WHAT.** Include alternatives considered with quantified rationale.

```
// 备注：决策：用 Channel 而非 Mutex
// 背景：20 goroutine 并发读写，峰值 10K+ 连接
// 方案 A: Mutex — 简单，但高并发下 15% 时间在锁等待
// 方案 B: Channel — 无锁争用，P99 延迟 120ms→35ms
// 结论：选 B
```

## System-Level Comments

Add for cross-cutting concerns: concurrency model, error propagation, data lifecycle, security boundaries. Focus on how pieces fit together, not implementation details.

## Verification

After editing, re-read the file to confirm all original English comments are preserved word-for-word. Zero code modified.
