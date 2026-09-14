---
schema: pdca.asset/v2
id: ontology:process/pdca-flow-model
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-11
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: 按当前真实状态进入，不自动从头跑流程
---

# 按当前真实状态进入，不自动从头跑流程

新工作先进行用户启用与创建授权，再由自己的Agent提出Plan目标。已有task先RECOVERY核对原身份、状态与待确认事项。读到技能、传了PDCA_ROOT、依赖ready均不等于启动。

| 用户操作／当前事实 | 进入 |
|---|---|
| 明确批准当前Plan请求 | flow-plan |
| 明确批准当前Do请求 | flow-do |
| 明确批准当前Check请求 | flow-check |
| 明确批准当前Act处置 | flow-act |
| 仅查询、恢复或无匹配批准 | 显示当前结果／待确认目标，不执行新的阶段 |
| 停止／撤权 | CONTROL安全收尾 |

每次获准阶段完成后保存事件与真实产物，返回awaiting_confirmation；不自动创建下一场景或新attempt。archived／interrupted只读。
