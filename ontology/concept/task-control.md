---
schema: pdca.asset/v2
id: ontology:concept/task-control
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: CONTROL-01：安全停止优先，等待不自动批准
---

# CONTROL-01：安全停止优先，等待不自动批准

默认等待用户操作无超时自动批准。用户可在任何阶段取消、撤权或暂停；收到可信停止后禁止新增业务动作，仅在原安全范围处理取消、对账和证据保全，不等待下阶段授权才能止损。

事件需原生来源和真实顺序；文件mtime、Agent填的时间不能决定审批与取消竞争。已批准阶段遇到后续撤权不能继续；不明顺序保持阻断。

父Agent不监工、不自动重试或接管。宿主可按真实事件路由、发出系统限制和安全终止，不审批业务目标。子任务各自与用户沟通；一处等待不阻碍无关已授权任务。

stopping到interrupted需真实结清／隔离依据；中止不补造未运行阶段。completed后消息只审计，不复活。新attempt另需用户操作和安全准入。
