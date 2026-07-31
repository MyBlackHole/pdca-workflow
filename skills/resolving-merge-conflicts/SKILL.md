---
name: resolving-merge-conflicts
description: Analyze and resolve Git merge conflicts in an AI agent context — identify conflict files, evaluate ours/theirs per hunk, apply resolution strategy, verify. Use when git merge or rebase reports conflicts.
---

Systematically resolve merge conflicts.

## Process

### 1. Identify
Run `git diff --name-only --diff-filter=U` to list conflicted files. Also check `git status` for unmerged paths.

### 2. Analyze each file
For each conflicted file:
- Dump conflict markers with `git diff` (shows ours/theirs/hunk boundaries)
- Count conflict blocks and their sizes
- Identify patterns: same-function edits, adjacent-line edits, text vs logic conflicts

### 3. Resolve per hunk
Apply one of these strategies per conflict block:

| Strategy | When | How |
|----------|------|-----|
| **ours** | Theirs is stale/wrong/experimental | Accept ours and remove conflict markers |
| **theirs** | Ours was superseded, theirs is the intended direction | Accept theirs |
| **manual merge** | Both sides have legitimate changes | Combine both, keeping intent |
| **defer** | Cannot determine correct resolution | Leave conflict markers with `// TODO: resolve` comment |

### 4. Verify
After resolving all files:
```bash
git diff --check          # No leftover conflict markers
git diff --stat           # Review what changed
```

If unsure about any block, leave it unresolved and note the file:line for human decision.

## Rules

1. Within one file, different hunks may use different strategies.
2. `git checkout --ours/--theirs <file>` restores the full file — use only when every hunk in the file uses the same strategy.
3. Never blindly accept ours or theirs across the entire repo.
4. If the conflict involves generated/lock files, prefer theirs (regenerate after).
5. After resolution, run the project's build/test command if available.