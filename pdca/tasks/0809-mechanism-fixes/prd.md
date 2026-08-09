# T0238 PRD — 机制修正：词汇契约适用范围 + 时间戳 guidance

## 问题陈述

T0234 实测发现两个 PDCA 机制问题：
1. **check-design-vocab 适用范围过宽**：design-it-twice 词汇契约校验器对任意
   stdin 文本都检查，导致 T0234 的 PRD（需求文档）被误报违规
   （component/service/API/boundary 是需求文本常见词）。契约应只约束接口
   设计文档。
2. **states 时间戳手工写入冲突**：T0234 手工写 states.plan（带微秒）晚于
   transition 自动写的 states.do（无微秒），datetime 比较 do<plan 触发
   STATE_TIME_ORDER（timestamps must be nondecreasing），但实际是手工写入
   与自动写入的冲突，校验层无明确 guidance。

## 方案

1. **check-design-vocab 场景限定**：新增 `--doc-type {design,other}` 参数
   （默认 design 检查）。doc-type 为 other 时跳过检查（vocab_ok=true 空违规）。
   调用方（design-it-twice 技能流程）以 design 调用；普通文档以 other 调用
   不误报。
2. **STATE_TIME_ORDER guidance 增强**：pdca_core 的 timeline_issues 在检测到
   时间序颠倒时，附加 guidance 指向 transition-phase 统一写入（明确禁止
   手工写 states 时间戳）。
3. **测试**：新增词汇契约场景限定测试（design 检查 / other 跳过）+
   STATE_TIME_ORDER 触发时的 guidance 断言。

## 验收标准

- [ ] AC-1: check-design-vocab 支持 `--doc-type` 参数，默认 design 检查
- [ ] AC-2: doc-type=other 时跳过检查（vocab_ok=true，空违规）
- [ ] AC-3: 现有 DesignVocabContractTest 不回归（design 检查行为不变）
- [ ] AC-4: STATE_TIME_ORDER 触发时 timeline_issues 返回明确 guidance
- [ ] AC-5: 新增测试覆盖场景限定与 guidance
- [ ] AC-6: 全量测试（PDCA 仓库）无回归

## 设计决策（用户确认）

- 按文档类型跳过（--doc-type 参数），非显式调用方参数
- 时间戳处理：校验层增强 guidance（非转换时重写），+ 测试
- 范围=仅脚本+测试（不改 flow 文档措辞）

## 关键取舍

- --doc-type 默认 design（保持现有行为，向后兼容）；other 显式跳过
- guidance 增强不改校验逻辑本身（避免放宽门禁）

## Seam 分析

### 声明的测试接缝
- seam: tests/test_mechanism_fixes.py -> scripts/check-design-vocab.py
- seam: tests/test_mechanism_fixes.py -> scripts/pdca_core.py

## 范围外

- flow 文档措辞更新、时间戳转换时重写、CI 集成
