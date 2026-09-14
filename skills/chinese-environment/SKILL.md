---
name: chinese-environment
description: Use when setting up a project for Chinese-speaking developers, or when all output (docs, comments, commits) should be in Chinese
---

# Chinese Environment (中文环境)

## Overview

Define the conventions for a Chinese-first development environment. **All AI thinking/reasoning and project-facing output uses Simplified Chinese**, while the code itself stays in English. This means analysis, planning, debugging reasoning, and all internal thought processes should be conducted in Chinese — not just the final output translated from English. Code annotation details are delegated to the `code-comments` skill.

## Core Rules

1. **AI 思考过程使用简体中文** — 内部推理、分析、规划、调试、代码审查等所有思考过程均使用简体中文，禁止先用英文思考再翻译成中文输出的方式
2. **All AI → user communication in Simplified Chinese** — explanations, suggestions, code reviews, Q&A
3. **Project documentation in Chinese** — README, API docs, changelog, spec documents, design docs
4. **Code stays in English** — variable names, function names, class names, type names, API signatures remain English
5. **Code comments in Chinese** — use `// 备注:` prefix; **REQUIRED SUB-SKILL:** also load `code-comments` for detailed annotation format rules; preserve original English comments
6. **Commit messages in Chinese** — follow conventional commits format: `类型: 中文描述`
7. **Project locale: China standard** — `zh_CN.UTF-8`, timezone `Asia/Shanghai`, encoding `UTF-8`

## Dimension Examples

### Documentation
```
<!-- 好：文档用中文 -->
# 用户积分管理系统
用户积分管理系统是一个用于追踪和管理用户积分的 Web 应用。

<!-- 不好：文档用英文（除非项目明确要求英文文档） -->
# User Points Management System
A web application for tracking user points.
```

### Code Comments
```
<!-- code-comments skill 负责具体格式，这里只声明原则 -->

// 备注：计算用户积分
// 备注：根据发帖数、评论数、认证状态计算，上限 1000 分
function calculateScore(user) { ... }
```

### Commit Messages
```
fix: 修复用户积分计算溢出问题
feat: 添加积分排行榜功能
docs: 更新 API 使用文档
refactor: 重构积分计算逻辑
```

## Common Mistakes

| Mistake | Why It's Wrong | Correct |
|---------|---------------|---------|
| 文档用英文写 | 中文环境项目文档应面向中文读者 | 所有项目文档用中文 |
| Commit message 用英文 | 与中文环境不一致 | `fix: 修复XX问题` |
| 把代码也翻译成中文（变量名、函数名） | 混入中文命名降低代码可移植性 | 代码保持英文，仅注释和文档用中文 |
| 用英文思考再翻译成中文输出 | 思考过程与输出语言脱节，导致表达生硬、不自然 | 从一开始就用中文思考，直接产生中文输出 |
| 注释和文档用了中文但忘记引用 code-comments | 缺少具体注释格式指导 | 引用 `code-comments` 处理注释细节 |

## Red Flags

- **"I'll write docs in English since code is in English"** — No. Documentation audience is separate from code audience.
- **"Chinese variable names are fine for this project"** — No. Keep code language-agnostic. Only comments and docs in Chinese.
- **"I already replied in Chinese, that's enough"** — Not enough. Internal thinking, documentation, commit messages, and code comments must also follow the rules.
- **"I'll handle comments however I want"** — No. Use `code-comments` skill for consistent annotation format.
- **"I think in English and translate to Chinese — same result"** — No. Thinking in English and translating degrades reasoning quality and makes Chinese output less natural. Think in Chinese from the start.

## Verification Checklist

- [ ] All AI thinking/reasoning (analysis, planning, debugging) is conducted in Simplified Chinese
- [ ] All documentation is in Simplified Chinese
- [ ] All code identifiers (variables, functions, classes, types) are in English
- [ ] Commit messages follow `类型: 中文描述` format
- [ ] Code comments reference `code-comments` skill or use `// 备注:` prefix
- [ ] Original English comments in code are preserved (per code-comments rules)
- [ ] locale and timezone are set to China standard
