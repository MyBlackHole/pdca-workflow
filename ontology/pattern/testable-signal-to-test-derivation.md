---
schema: pdca.asset/v2
id: ontology:pattern/testable-signal-to-test-derivation
type: pattern
semantic_kind: individual
layer: Knowledge
status: active
authority: reference
revision: 3.1.0
summary: 从信号派生可观察测试
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
relations:
  instance_of:
  - ontology:pattern
  relates_to:
  - ontology:concept/pdca-acceptance-criterion
  - ontology:concept/pdca-evidence
  - ontology:concept/ontology-rule-attr-testable
validation:
  claim_status: unverified
  adoption: claim_review_required
provenance:
  pre_review_revision: 2.0.0
---

# 从信号派生可观察测试

每个测试先写输入/动作、可观察事实、预期与失败条件，再选择宿主已有工具执行。

| 层级 | 示例 | 不能证明什么 |
|---|---|---|
| 结构 | 删除必需字段后检查应报缺失；构造悬空ID应定位 | 不能证明用户已授权或业务行为成功 |
| 行为 | 无确认时不进入Do；工具实际失败时不得pass | 模拟判断不能代替真实宿主隔离/执行 |
| 授权 | 重放旧task/旧digest确认应拒绝；核验真实来源 | 纯文本authority字段不能证明身份 |
| 效果 | 固定任务集比较返工/成功率 | 单个静态扫描不能推断性能提升 |

AC映射本身不作为通过证据。没有执行工具时保存测试设计并标not_run。参考根tests/behavior-cases.md的反例，必须记录预期和实际，不只统计是否提到“测试”。
