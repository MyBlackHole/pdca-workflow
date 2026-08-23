---
schema: pdca.asset/v1
id: T0375-0823-interaction-capture
phase: check
source_ids: [grilling-after, flows-after, smoke, feedback-log, audit-clean, convergence-map-v2]
---

## 上下文

T0374 审查后由用户元反馈直接立项：修复真实交互流失与 AI 代填污染。方案吸收 mattpocock/skills 五种关联模式（经用户问询触发核实），provenance 双态标记为双方空白即本项目超越点。

## 假设与结果

| 假设 | 结果 |
|------|------|
| H1 新字段不破坏现有门禁 | 成立：schema 未锁 additionalProperties，冒烟双类型通过，append-confirmation 实测正常 |
| H2 三条元反馈可补录 | 成立：4 条 user_meta_feedback(captured:true) 已入 T0375 JSONL 可检索 |
| H3 流程约定即可生效（无需改平台工具） | 待观察：captured 标记依赖执行纪律，需下个任务的 grill 实测检验 |

## 分析（逐 AC 判定）

- **AC-1** ✅ grilling SKILL：规则 7 provenance 双态+HITL 红线、规则 8 防重问、已知坑补元反馈落盘（grilling-after）。
- **AC-2** ✅ flow-plan P6 与 flow-check Ch5 各含自由文本反馈落盘要求（flows-after）。
- **AC-3** ✅ 冒烟测试双类型零 issue（smoke）；direction_confirm 经 append-confirmation 正常追加。
- **AC-4** ✅ 4 条 user_meta_feedback(captured:true) 含用户三条原话逐字记录（feedback-log）。
- **AC-5** ✅ baseline 豁免三文件（grilling 4620B/flow-plan 4751B/flow-check 2912B），audit 零 budget issue（audit-clean）。

## 适用边界

- captured 标记的真实性最终靠执行纪律保障，机制上仍可能被违规标 true——数据层无法完全防伪。
- 历史存量（657 条代填问答）未清洗，检索交互语料时须过滤 `captured:true` 才可信。

## 失败原因

不适用。

## 下一轮建议

1. 下个含 grill 的任务实测"防重问规则"与"captured 标记"的执行摩擦，若频繁漏标考虑在 transition 门禁加软提示。
2. user_meta_feedback 积累到 10 条后可做一次模式归纳（用户偏好深度/广度的量化画像）。
