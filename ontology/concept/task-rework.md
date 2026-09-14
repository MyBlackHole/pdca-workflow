---
schema: pdca.asset/v2
id: ontology:concept/task-rework
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: REWORK-01：返工由用户选择
---

# REWORK-01：返工由用户选择

阶段内原范围的必要调试／重试可由原Agent自主进行，保留失败证据和停止预算，不放宽oracle。缺少权限或需要扩大目标先沟通。

Check发现业务违例：保留报告，提出修复范围及下一次Do的目标；用户明确启动新的Do run后才能修改，再重新请求Check和Act。原task／attempt／Agent可保持，前提是目标、冻结oracle与身份未变。旧run与确认不可覆盖，固定序列按事件递增而非伪造四条边。

目标／oracle／定义版本或Agent变化、终态任务重做：用户明确批准新attempt，原尝试安全结束，使用新独立Agent且从Plan目标沟通开始。新场景同样不能自动启动。

被审projection错误时，verification任务只报告；不能修改被审对象冒充验证通过。用户为projection安排新的修复任务／attempt，并对新产物重新进行必要审查。
