---
schema: pdca.asset/v1
id: ontology:domain/skill-prototype
name: prototype
summary: Create prototypes to validate assumptions before full implementation.
description: Build a throwaway prototype to answer a design question — a single shareable HTML file for state/logic questions, or several radically different UI variations toggleable from one route. Capture on a throwaway branch. Use when the question is "does this design feel right?" or "what should this look like?".
invocation: model-invoked
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-prototype/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/design-tree
    - ontology:concept/domain-model
    - ontology:domain/skill-research
    - ontology:concept/skill-mechanics
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# Prototype — 模型驱动的快速原型验证

model-invoked：AI 自动构建 throwaway 原型回答设计问题，捕获到 throwaway branch。

## 触发条件

当问题为 "does this design feel right?" 或 "what should this look like?" 时触发。

## Pick a branch

- **Logic / state model** → build a single self-contained HTML file (plain HTML/CSS/JS, no build, no server) exercising the core state machine. Non-developers can open by double-click and drive in their own domain language: labelled state panel, always-available free-play buttons, tabbed guided walkthroughs.
- **UI / look & feel** → generate several radically different UI variations on a single route, switchable via a URL param.

## Rules

1. **Clearly marked as throwaway.** Locate next to the code it's prototyping; name so it's obviously not production.
2. **One command to run.** Use the project's existing runner.
3. **No persistence.** State lives in memory unless the question itself is about persistence.
4. **No polish.** No tests, no error handling beyond runnability, no abstractions.
5. **Surface state.** After every action (logic) or on every variant switch (UI), show the full relevant state.
6. **Capture on throwaway branch.** Commit prototype to `prototype/<name>` throwaway branch (out of main) and leave a context pointer on the implementation issue. Do not delete — the prototype is captured as runnable evidence.
7. **Answer persists.** Verdict + question captured durably in issue/ADR/commit.

## Throwaway Branch 策略

- **分支命名**：`prototype/<name>`，明确标识为原型而非生产代码
- **不在 main 上修改**：所有原型提交到 throwaway branch
- **Context pointer**：在实现问题上留下 context pointer，关联原型证据
- **自动清理**：原型验证完成后，throwaway branch 可保留作为证据，但不合并到 main

## Exit

Question answered and validated decisions folded into real code. Prototype committed to throwaway branch with context pointer.

## 已知坑

- throwaway 原型回答完设计问题即弃，勿演化为生产代码——它未经过生产级审查。
- 原型不再删除：捕获为可运行证据在 `prototype/<name>` throwaway branch 上，在实现问题上留下 context pointer。
- model-invoked 模式下，AI 自动构建原型，用户只需验证结果。