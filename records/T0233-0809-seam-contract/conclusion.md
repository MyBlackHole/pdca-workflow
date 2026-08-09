---
schema: pdca.asset/v1
id: T0233-0809-seam-contract
phase: check
source_ids: [flow-plan-p35, spec-seam-section, seam-contract-impl, seam-contract-tests-v2, context-seam-terms, adr-0018]
---

# Conclusion — seam 确认门禁 + PRD seam 契约

## 上下文

穷尽审查 mattpocock/skills 全部 37 个技能后，确认 to-spec 的"先 sketch
测试接缝 → 与用户确认 → 再写 spec"是唯一剩余实质可证明提升。PDCA 原 seam
确认推迟到 Do 阶段兜底（tdd 技能），返工成本高。用户确认落地 seam 契约。

## 假设与结果

| 假设 | 结果 |
|------|------|
| flow-plan 新增 P3.5 seam 确认步骤（P3 后 P4 前） | ✅ AC-1 通过 |
| SPEC.md 定义 `### 声明的测试接缝` 子节 + `- seam:` 行格式 | ✅ AC-2 通过 |
| 契约测试断言 seam 测试文件存在 | ✅ AC-3 通过（test_missing_test_file_fails） |
| 契约测试断言被测模块与声明一致 | ✅ AC-4 通过（test_missing_target_reference_fails） |
| 无 seam 行 spec 跳过（不追溯） | ✅ AC-5 通过（test_no_seam_lines_returns_empty） |
| 全量测试无回归 | ✅ AC-6 通过（130 passed + 13 subtests） |

## 分析

- **可证明性**：seam 契约同构 T0231 source 术语契约、T0232 词汇契约——
  机器可读清单（`- seam:` 行）+ 契约测试守护。12 个新测试覆盖解析、
  文件存在、模块一致、无 seam 行跳过四类边界。
- **流程提前**：seam 确认从 Do 阶段兜底（tdd）提前到 Plan P3.5，减少返工；
  P6 门禁检查子节存在双保险。
- **范围限定**：仅 development/bugfix 场景（有测试产物）；research 等无测试
  产物不强制，避免假阴性。
- **审查修正**：A4 审查发现测试与实现重复定义 parse_seams，改为测试引用实现
  的纯函数，消除漂移风险。

## 适用边界

- 契约只约束新 spec（无 `- seam:` 行即跳过），不追溯历史。
- P3.5 负责用户展示确认，P6 负责结构门禁。
- seam 契约是文件级/模块级一致性校验，不校验测试质量。

## 下一轮建议

- 若未来引入实际并行调度，ready-set batches（T0232）可直接驱动。
- seam 契约可在 CI 中作为门禁：运行 `scripts/seam_contract.py` 校验每个
  development spec。
- mattpocock/skills 可证明空间经 T0230-T0233 四轮已系统收割，后续新候选
  需重新审查其技能更新。
