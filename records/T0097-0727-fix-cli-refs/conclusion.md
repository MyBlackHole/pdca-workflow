---
schema: pdca.asset/v1
id: T0097-0727-fix-cli-refs
layer: experience
summary: 修复 knowledge/pdca-flow 中遗留的死 CLI 引用
tags: [knowledge, cleanup, stale-content]
---

# 结论: T0097 — 修复死 CLI 引用

## 改动
- architecture.md: 替换 CLI 命令块为当前手动创建方式（skills/ + flows/ 文件操作）
- cli-behavior.md: 整体重写为项目操作约定（SKILL.md 编辑规则、提交策略、ID 单调递增）
- manifest.jsonl: revision 2 条目（新内容摘要）

## 根因
architecture.md 和 cli-behavior.md 创建于初始 feat commit，一直未随 CLI 废弃而更新。
