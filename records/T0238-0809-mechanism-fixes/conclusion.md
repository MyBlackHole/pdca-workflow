---
schema: pdca.asset/v1
id: T0238-0809-mechanism-fixes
phase: check
source_ids: [vocab-scope, time-guidance, mechanism-tests, convergence-map]
---

# Conclusion — 机制修正：词汇契约场景限定 + STATE_TIME_ORDER guidance

## 上下文

T0234（FastAPI 应用验证 PDCA 流程）实测发现两个 PDCA 机制问题，本任务修复：
1. check-design-vocab 对需求文本误报（component/API 等通用词），契约应只
   约束接口设计文档。
2. 手工写 states 时间戳（带微秒）与 transition 自动写（无微秒）冲突，
   触发 STATE_TIME_ORDER 误判，校验层无明确 guidance。

## 假设与结果

| 假设 | 结果 |
|------|------|
| check-design-vocab 加 --doc-type 场景限定 | ✅ AC-1/AC-2：design 检查、other 跳过（vocab_ok=true 空违规） |
| 现有 design 检查行为不回归 | ✅ AC-3：DesignVocabContractTest 仍通过（默认 design 向后兼容） |
| STATE_TIME_ORDER 触发时返回 guidance | ✅ AC-4：guidance 指向 transition-phase，明确禁止手工写 states 时间戳 |
| 新增测试覆盖 | ✅ AC-5：test_mechanism_fixes.py 7 测试（doc-type 两分支 + guidance 断言） |
| 全量无回归 | ✅ AC-6：137 passed + 13 subtests，doctor valid |

## 分析

1. **场景限定解决了误报根因**：词汇契约是 design-it-twice 的产出约束，本应
   只校验接口设计文档。--doc-type other 让 PRD/需求文本显式跳过，不误报。
   默认 design 保持向后兼容（design-it-twice/SKILL.md 调用无需改）。

2. **guidance 增强而非放宽门禁**：STATE_TIME_ORDER 校验逻辑不变，仅附加
   guidance（"never hand-write states timestamps" + 指向 transition-phase）。
   触发者得到明确修复指引，门禁强度未降。

3. **真实流程摩擦点发现**（T0238 自身 Plan→Do 经历）：plan→do 转换要求
   states.plan 已打时间戳，但初始创建时无 plan 时间戳。transition 从
   final_confirmation 时间锚点后仍需人工对齐——这是未来可改进点
   （transition 自动补写 plan 时间戳）。

## 适用边界

- 词汇契约仅约束设计文档（doc-type=design）；其他文档需显式传 other 跳过。
- guidance 只改善错误提示，不改变校验逻辑或时间戳要求。

## 下一轮建议

- transition 自动补写 states.plan 时间戳（消除人工对齐摩擦）。
- seam_contract + 本任务成果可集成 CI 门禁。
