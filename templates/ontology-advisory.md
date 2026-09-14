---
schema: pdca.ontology-advisory/v1
state: draft
protocol_revision: 3.4.11
notice_id: null
library_id: null
issuer_ref: null
source_ref: null
sequence: null
affected_definitions: []
affected_constraint_ids: []
evidence_refs: []
severity: null
recommended_action: null
replaces_notice_ref: null
status: null
scope_limitations: []
---

# 定义可信性公告

ADOPT-01。公告独立于不可变定义字节：affected_definitions明确ID/revision/digest或可验证版本集合，不能只说“以前的都错”。status为proposed/issued/revoked；issued需真实发行者/依据，未授权内容不能改写目标。

真实严重错误可阻断当前采用/执行/发布，但普通新版本通知不使全部旧树失效。撤销公告需明确权限、证据和替代关系，不能由受影响实现Agent自行删除。并发发布前要按实际宿主控制边界复核notice视图，缺关键事实则unknown/blocked。

传递通知需遵守工作权限；不得将私有任务的原始对话/数据发布到公共知识库。
