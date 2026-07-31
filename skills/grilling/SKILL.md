---
name: grilling
description: Interview the user relentlessly about a plan, design, or conclusion — one question at a time, each with a recommended answer. Walks the decision tree until every branch is resolved. Use when the user needs to stress-test their thinking, during Plan→Do alignment, or before writing a conclusion.
---

Interview the user relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one.

## Core rules

1. **One question at a time.** Never batch multiple questions.
2. **Each question with your recommended answer.** "I suggest X because Y. Do you agree?"
3. **Walk the decision tree.** Each answer determines the next branch. Don't pre-guess.
4. **Verifiable facts are not questions.** Look up what can be checked via filesystem, code analysis, or tools.
5. **Only ask decisions the user can make.** Trade-offs, priorities, design choices.
6. **Log every Q&A** to `clarifications.jsonl` with `source: "grilling"`: `{"round": N, "question": "...", "answer": "...", "recommended": "...", "source": "grilling", "at": "..."}`.

## Viewpoints by context

### Plan→Do (reviewing prd.md / design.md)
- What boundary conditions are missed?
- Under what scenarios does this assumption break?
- Was the rejected alternative sufficiently justified?
- Are acceptance criteria testable and measurable?

### Do→Check (reviewing evidence + activities)
- Is the conclusion adequately supported?
- Are there alternative explanations not ruled out?
- Are critical paths tested?
- Any unexposed performance/security trade-offs?

### Check→Act (reviewing conclusion.md + verdict)
- What are the limits of this conclusion?
- What parts are reusable knowledge?
- What process improvements for next time?

## Exit

- All branches walked → summarize alignment to user. Format:
  ```
  我理解的目标是：<目标>
  范围：<范围>  
  方案方向：<方向>
  关键决策：<已确认的取舍>
  以上理解是否正确？
  ```
- User confirms → alignment complete, proceed.
- User revises → continue grilling until aligned.
- Blocking issue found → state the blocker, suggest returning to prior phase.

## Collaboration with domain-modeling

Fuzzy terms → update `$PDCA_HOME/pdca/CONTEXT.md` immediately.
Irreversible decisions → create ADR in `$PDCA_HOME/docs/adr/`.