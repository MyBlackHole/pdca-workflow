---
name: grilling
description: Interview the user relentlessly about a plan, design, or conclusion — in rounds, asking the whole frontier of answerable decisions each round, each with a recommended answer. Walks the decision tree until every branch is resolved. Use when the user needs to stress-test their thinking, during Plan→Do alignment, or before writing a conclusion.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## Core model

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question formatted like so:

```
❓ Q1 - <question title>: <question body, might be multiple paragraphs, including multiple choices>
➡️ <your recommended answer>
```

Each round, the answers reshape the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

## Core rules

1. **Ask the whole frontier each round, never one-at-a-time.** Every currently-answerable decision goes into the current round; batch them all, each with a recommended answer.
2. **Each question with your recommended answer.** "I suggest X because Y. Do you agree?"
3. **Walk the decision tree.** Each answer determines the next branch. Don't pre-guess.
4. **Verifiable facts are not questions.** Look up what can be checked via filesystem, code analysis, or tools. When a frontier question needs a fact, dispatch a sub-agent or check the environment yourself — never ask the user for anything you could look up.
5. **Only ask decisions the user can make.** Trade-offs, priorities, design choices.
6. **Log every Q&A** to `clarifications.jsonl` with `source: "grilling"`: `{"round": N, "question": "...", "answer": "...", "recommended": "...", "source": "grilling", "at": "..."}`. All questions in the same round share the same `round` number; each question is its own JSONL line.

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

- Frontier empty — every branch of the design tree visited, nothing left silently assumed → summarize alignment to user. Format:
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
