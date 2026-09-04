---
schema: pdca.asset/v1
id: ontology:concept/external-evidence-collection
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/external-evidence-collection/1.0.0
summary: 外部项目产物须先复制到中央 workspace external-artifacts 再登记 Evidence
relations:
  specializes:
  - ontology:concept/pdca-evidence
  relates_to:
  - ontology:concept/pdca-evidence
---

# 外部证据收集协议（external-evidence-collection）

中央 Evidence manifest 只接受 workflow root 内的安全相对路径，拒绝绝对路径与符号链接。外部 agent 产物按以下顺序处理：

1. 原件保留在业务项目目录。
2. 复制副本到 `workspace/external-artifacts/`。
3. 使用 `register-evidence` skill 或手动写入 `manifest.jsonl` 登记证据。
4. 在 Experience 中引用 Evidence ID，不把完整报告复制进经验。

执行器应把复制目录与命令模板作为受控能力提供，避免 agent 自行创建根目录 `evidence/` 或反复请求跨目录权限。

## 来源

- `（原知识层）external-evidence-collection.md`
