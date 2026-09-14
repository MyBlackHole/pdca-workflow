---
schema: pdca.asset/v2
id: ontology:concept/pdca-gate
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: GATE-01：启动资格与完成判定分开
---

# GATE-01：启动资格与完成判定分开

每次阶段开始同时检查：用户启动请求及真实消费；原task/attempt/Agent/run匹配；固定输入和计划版本未变；上一阶段完成及必要依赖；无取消／撤权；真实写域和工具可用。只要一项不足就阻断本次动作，不自动改目标。

| 目标阶段 | 主要输入 | 不能替代授权的事实 |
|---|---|---|
| Plan | 用户沟通后的目标、seed、范围、预期本体／实体 | 用户仅说“优化”、已创建Agent |
| Do | 已完成Plan、冻结验收、获准写域及计划版本 | Plan看起来合理、测试模板存在 |
| Check | 已完成Do run、最终产物清单、冻结验收及证据 | 工具退出0、Do完成 |
| Act | 当前Check报告及对应产物、具体处置范围 | 所有AC为PASS、父Agent建议 |

Check可以诚实发现fail或unknown并完成；允许用户批准Act进行失败归档／提出返工，但不能将失败对象标为可用。缺失必需本体源／映射不允许delivery_usable=true，允许记录失败及限制。

阶段内的授权动作不需要逐工具确认；变更目标／写域／oracle或做新的不可逆操作必须重新沟通。生成下一阶段请求是沟通，不是启动该阶段。
