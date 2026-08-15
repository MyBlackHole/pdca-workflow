---
name: handoff-work
description: Write a compact, redacted handoff record for a future session or agent.
---

Write a handoff document summarising the current conversation.

Write to `$PDCA_HOME/records/<record-id>/handoff.md`:

```markdown
## 当前状态
## 未完成事项
## 已知约束
## 推荐的下一步
## 关键上下文文件列表
```

Include a "suggested skills" section recommending skills the next session should load.

Do not duplicate content captured in other artifacts (specs, plans, ADRs, commits). Reference them by path instead.

Redact sensitive information (API keys, passwords, PII).

## 已知坑

- 记录须 compact 且保留决策链，供未来 session 恢复上下文；冗余细节会稀释可恢复性。
