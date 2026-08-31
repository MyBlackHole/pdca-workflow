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
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/design-tree
    - ontology:concept/domain-model
    - ontology:domain/skill-research
---

--

name: prototype
description: Build a throwaway prototype to answer a design question — a single shareable HTML file for state/logic questions, or several radically different UI variations toggleable from one route. Capture on a throwaway branch. Use when the question is "does this design feel right?" or "what should this look like?".
---

Build throwaway code that answers a single question, then capture the answer on a throwaway branch.

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

## Exit

Question answered and validated decisions folded into real code. Prototype committed to throwaway branch with context pointer.

## 已知坑

- throwaway 原型回答完设计问题即弃，勿演化为生产代码——它未经过生产级审查。
- 原型不再删除：捕获为可运行证据在 `prototype/<name>` throwaway branch 上，在实现问题上留下 context pointer。