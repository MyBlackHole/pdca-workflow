---
schema: pdca.ontology-release/v1
state: draft
protocol_revision: 3.4.10
manifest_id: null
library_id: null
definition_id: null
revision: null
payload_ref: null
payload_digest: null
semantic_identity: null
applicability: null
adoption_restrictions: null
definition_dependencies: []
term_dependencies: []
case_dependencies: []
closure_entries: []
closure_complete: null
origin_proposal_id: null
---

# 固定知识发布清单

EVOLVE-01。每个closure_entries项含entry_id、kind、ref、revision、digest、直接依赖ID；共同依赖只列一次，缺项/异字节/不可重读则阻断。清单固定最终payload及实际语义闭包，不把relates_to全库拉入。

origin_proposal_id只存预先分配的候选逻辑身份，不保存候选文件摘要，避免候选引用manifest而manifest又引用候选摘要的循环。清单不保存自己的digest、未来review/authorization/publication receipt。

payload中的active、revision或验证标签都不是发布证明。清单不能把未核验事实升级成已验证，也不能将候选模板当作真实已发布内容。实际摘要由外部引用计算和保存。
