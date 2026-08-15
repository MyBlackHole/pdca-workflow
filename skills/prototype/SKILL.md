---
name: prototype
description: Build a throwaway prototype to answer a design question — a runnable terminal app for state/logic questions, or several radically different UI variations toggleable from one route. Use when the question is "does this design feel right?" or "what should this look like?".
---

Build throwaway code that answers a single question, then capture the answer.

## Pick a branch

- **Logic / state model** → build a tiny interactive terminal app exercising the core state machine through hard-to-reason-about cases.
- **UI / look & feel** → generate several radically different UI variations on a single route, switchable via a URL param.

## Rules

1. **Clearly marked as throwaway.** Locate next to the code it's prototyping; name so it's obviously not production.
2. **One command to run.** Use the project's existing runner.
3. **No persistence.** State lives in memory unless the question itself is about persistence.
4. **No polish.** No tests, no error handling beyond runnability, no abstractions.
5. **Surface state.** After every action (logic) or on every variant switch (UI), show the full relevant state.
6. **Capture when done.** Fold validated decisions into real code. Commit prototype to a throwaway branch (out of main) and leave a context pointer on the task.

## Exit

Question answered and validated decisions folded into real code. Prototype committed to a throwaway branch.

## 已知坑

- throwaway 原型回答完设计问题即弃，勿演化为生产代码——它未经过生产级审查。
