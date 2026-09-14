---
schema: pdca.asset/v2
id: ontology:concept/work-dependency-graph
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: DEPENDENCY-01：数据依赖不是用户授权
---

# DEPENDENCY-01：数据依赖不是用户授权

图记录任务输入和产物依赖，组成树另表父子；固定图版本及必需节点。每项输入必须能解析到固定产物及其可用性，不能仅依据目录或PASS字段。

有向依赖无环；父modeling不等待未创建孩子，projection组合等真实孩子交付。一个节点失败只影响实际依赖范围，等待确认不形成全局锁。

输入ready只说明可提出启动建议；没有用户操作不能自动创建／推进。修改源版本使依赖证据stale，不能沿用旧组合与审查结论。
