---
schema: pdca.asset/v2
id: ontology:concept/task-unit-test
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: TEST-01：验收标准必须被实际观察支持
---

# TEST-01：验收标准必须被实际观察支持

Plan固定用户目标对应的AC、测试对象、预期oracle和必要正反例；测试数量、存在性和退出0不能替代行为证明。阶段内每次实际run记录输入版本、工具、输出及局限。

modeling检查模型对象／关系／约束、目标覆盖、来源与负例；projection检查实际行为及source→target映射；verification对固定模型和产物独立核对，并区分对象失败与检查器失败。

只验证链接和摘要不能证明语义。没有工具或外部系统时保留unknown／not_run，不自填PASS。改变产物后重跑受影响检查与全部必需回归；原失败日志保留。
