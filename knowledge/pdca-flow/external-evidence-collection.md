---
schema: pdca.asset/v1
id: knowledge:pdca-flow/external-evidence-collection
layer: knowledge
summary: 外部项目产物必须先复制到中央 workspace external-artifacts 再登记 Evidence
tags: [evidence, centralized-management, opencode, executor]
scenarios: [default, research]
phases: [do, check, act]
applies_when: [agent 在 workflow root 外生成报告或日志]
excludes_when: [产物本身已经位于 workflow root 内]
source_ids: [experience:T0026--07-26-opencode-调研-bcachefs-并输出中央文档]
confidence: high
status: active
---

# 外部证据收集协议

中央 Evidence manifest 只接受 workflow root 内的安全相对路径，拒绝绝对路径和符号链接。外部 agent 产物应按以下顺序处理：

1. 原件保留在业务项目目录。
2. 复制副本到 `workspace/external-artifacts/`。
3. 使用 `register-evidence` skill 或手动写入 `manifest.jsonl` 登记证据。
4. 在 Experience 中引用 Evidence ID，不把完整报告复制进经验。

执行器应把复制目录和命令模板作为受控能力提供，避免 agent 自行创建根目录 `evidence/` 或反复请求跨目录权限。
