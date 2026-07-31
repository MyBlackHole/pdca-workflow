---
schema: pdca.asset/v1
id: T0098-0727-clean-knowledge
layer: experience
summary: 清理 knowledge 中 3 个文件的残留死 CLI 和过期描述
tags: [knowledge, cleanup, stale-content]
---

# 结论: T0098 — 清理 knowledge 旧内容

## 改动

| 文件 | 处理 | 行数变化 |
|------|------|---------|
| `pdca-flow/global-repo-config.md` | 重写：pdca init → PDCA_HOME + init-external.sh | 20→34 |
| `pdca-flow/generic-ai-workflow-kernel.md` | 精简：弃用未落地 Rust CLI 设计，保留原则 | 100→40 |
| `pdca-flow/external-evidence-collection.md` | 小修：task add-evidence → register-evidence | 25→25 |

## 根因
遗留文件的创建时间都早于去 CLI 化（T0087-T0090），从未随系统演化更新。
