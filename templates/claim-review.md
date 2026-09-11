---
schema: pdca.claim-review/v1
claim_id: null
node_id: null
node_revision: null
claim_text: null
claim_kind: null
scope: null
source_refs: []
source_version: null
source_locator: null
checked_level: null
decision: null
evidence_refs: []
adopted_constraint_ids: []
known_limits: []
protocol_revision: 3.4.10
---

# 逐主张采用记录

claim_kind=design/fact/inference；checked_level遵循ONTOLOGY-01。design定位真实用户目标，fact定位一手来源/版本，inference记录推导与不确定性。decision=accept/reject/unknown，只对本条scope生效。

源文件字节未取得时不能虚构sha256；可以记录网页访问及明确段落，后续实现任务仍需固定实际源码/规范。关键词出现、示例数量、报告自述均不构成行为证据。

写明正确样本、错误定义/错误实现反例、oracle独立性与真实运行状态。隔离节点解除必须新revision和相应回归。
