# 技能索引

PDCA 工作流所有可用技能一览。

| 名称 | 类型 | 行数 | 被引用次数 | 描述 |
|------|------|------|-----------|------|
| advance-phase | model-invoked | 12 | 8 | Update task.json meta.phase to the next phase and set relevant timestamps. Use when transitioning between PDCA phases. |
| ask-matt | user-invoked | 30 | 0 | 根据你的描述，推荐合适的 PDCA 入口。初次使用或不确定从哪开始时，从这里入手。 |
| bug-analysis | model-invoked | 15 | 0 | 用于缺陷、异常和回归问题的根因分析；先收集证据，再区分假设、实验和过程原因。 |
| bug-commit-format | model-invoked | 33 | 1 | Use when fixing bugs and committing changes — commit messages must include bug description, root cause, solution, impact scope, and performance impact |
| build-config | model-invoked | 47 | 0 | Use when setting up build configuration for new projects, adding/managing dependencies, or switching between C/C++/Rust/Go/Python build systems |
| chinese-environment | model-invoked | 78 | 0 | Use when setting up a project for Chinese-speaking developers, or when all output (docs, comments, commits) should be in Chinese |
| code-comments | model-invoked | 58 | 0 | Use when adding Chinese annotation comments to code, when asked to translate/add supplementary comments in Chinese to existing code, or when needing to embed business-understanding diagrams (ASCII / Mermaid) alongside source code for clearer business logic visualization, or when documenting technical principles / architecture decisions / algorithm mechanisms / system architecture understanding inline for deeper code comprehension |
| code-review-checklist | model-invoked | 32 | 0 | Use when conducting code reviews, reviewing pull requests, or performing quality assurance on C, C++, Rust, Go, or Python code |
| code-review | model-invoked | 91 | 3 |  |
| commit-format | model-invoked | 83 | 0 |  |
| context-retrieval | model-invoked | 57 | 0 | 按任务场景、阶段、标签和来源链选择最小可信 AI 上下文 |
| diagnosing-bugs | model-invoked | 55 | 1 | Structured diagnosis loop for hard bugs and performance regressions — build a tight feedback loop, reproduce, hypothesise, instrument, fix, regression-test. Use when the user reports something broken, throwing, failing, or slow. |
| domain-modeling | user-invoked | 82 | 4 |  |
| feature-commit-format | model-invoked | 31 | 0 | Use when implementing new features and committing changes — commit messages must include requirement description, background, implementation, impact scope, and testing verification |
| grilling | model-invoked | 52 | 5 | Interview the user relentlessly about a plan, design, or conclusion — one question at a time, each with a recommended answer. Walks the decision tree until every branch is resolved. Use when the user needs to stress-test their thinking, during Plan→Do alignment, or before writing a conclusion. |
| grill | user-invoked | 6 | 1 | Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved. |
| handoff | user-invoked | 22 | 1 | Compact the current conversation into a handoff document so another agent (or a future session) can continue the work. Use when wrapping up a session mid-task or passing to another agent. |
| prototype | model-invoked | 23 | 2 | Build a throwaway prototype to answer a design question — a runnable terminal app for state/logic questions, or several radically different UI variations toggleable from one route. Use when the question is "does this design feel right?" or "what should this look like?". |
| register-evidence | model-invoked | 18 | 7 | Copy task artifacts into records/<record-id>/evidence/ and append to manifest.jsonl. Use when completing a Do or Check step that produces artifacts. |
| research | model-invoked | 19 | 2 | Investigate a question against high-trust primary sources and capture findings as a cited Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered. |
| secure-coding | model-invoked | 37 | 2 | Use when reviewing code for security vulnerabilities, implementing security-critical logic, or auditing C/C++/Rust/Go/Python code |
| testing-strategy | model-invoked | 51 | 1 | Use when designing test plans, deciding what/how to test, choosing testing tools and frameworks, or reviewing test coverage for C, C++, Rust, Go, or Python projects |
| triage | user-invoked | 53 | 1 |  |
| verify-convergence | model-invoked | 12 | 1 | Check that all required evidence listed in task.json meta.convergence are present in evidence/manifest.jsonl. Use before writing conclusion. |
| wayfinder | user-invoked | 36 | 0 |  |
| wayfinding-chart | model-invoked | 53 | 1 | 绘制 Wayfinder 决策地图。由 wayfinder 委托加载，不直接调用。 |
| wayfinding-work | model-invoked | 26 | 1 | 推进已有 Wayfinder 地图，每 session 解决一张决策票。由 wayfinder 委托加载，不直接调用。 |
| web-research | model-invoked | 28 | 0 | 网络资料调研辅助技能。当实验阶段的场景为网络调研时，提供问题拆解、搜索策略、信息整理和结论输出的结构化指导。 |
| write-conclusion | model-invoked | 34 | 1 | Write records/<record-id>/conclusion.md with structured findings, then record verdict in task.json. Use at end of Check phase. |
| writing-great-skills | user-invoked | 76 | 0 | 参考指南——如何编写和维护高质量的 PDCA 技能文件。定义了信息层级、极简原则、拆分规则和失败模式。 |

---
*自动生成于 2026-07-27*
