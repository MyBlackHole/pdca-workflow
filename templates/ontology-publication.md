---
schema: pdca.ontology-publication/v1
state: draft
protocol_revision: 3.4.10
publication_id: null
proposal_id: null
library_id: null
definition_id: null
revision: null
manifest_ref: null
manifest_digest: null
payload_digest: null
base_revision: null
base_digest: null
base_manifest_digest: null
expected_absent: null
catalog_before_generation: null
catalog_before_digest: null
catalog_after_generation: null
previous_publication_ref: null
review_refs: []
authorization_ref: null
request_decision_ref: null
authorization_action: null
resource_reservation_ref: null
backend_commit_ref: null
outcome: null
reason: null
actor_ref: null
---

# 知识发布提交或拒绝回执

EVOLVE-01。outcome为committed/rejected/unknown；只有真实提交事实可写committed。authorization_action应明确publish_definition及library/definition/manifest/base范围；普通Check认可不够。合成fixture不能写作真实用户来源。

提交边界必须同时比较catalog generation/digest与定义head/base；create确认不存在。post generation为真实提交顺序，不猜时间或文件mtime。rejected保留已观察head与理由，不能改成通过。unknown先核查实际提交，不盲目重放。

若使用单写者追加日志，本回执必须来自其完整提交边界或引用真实backend_commit；head和ontology投影仅可重建视图。无跨文件原子能力不能宣称全部存储对象原子。回执不在自身正文计算自己的摘要。
