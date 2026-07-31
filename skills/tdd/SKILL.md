---
name: tdd
description: Test-driven development. Use when building features or fixing bugs test-first, or when asked to follow "red-green-refactor" cycle.
---

# TDD — 测试驱动开发

TDD 是红→绿循环。本技能确保循环产出值得保留的测试：好测试的标准、测试边界（seam）、抗模式、循环纪律。

进入 TDD 循环前，阅读 `pdca/CONTEXT.md`（如有）以对齐测试命名和领域术语，并查阅 `docs/adr/` 了解该区域的架构决策。

## 好测试的标准

测试通过**公共接口**验证行为，而非实现细节。代码可以完全重写，测试不应变化。好测试读起来像规格说明 —— `"user can checkout with valid cart"` 精确描述了存在的能力，重构时仍然存活。

代码示例见 [tests.md](tests.md)，Mock 策略见 [mocking.md](mocking.md)。

## Seam — 测试边界

**Seam（接缝）** 是测试的公共边界：在不深入内部的前提下观察行为的接口。测试写在各 seam 上，绝不针对内部实现。

**只能在预先约定的 seam 上写测试。** 写任何测试前，先列出待测 seam 并与 AI 确认。未经确认的 seam 不写测试。你不可能测试一切 —— 预先约定 seam 才能把测试投入落在关键路径和复杂逻辑上，而非覆盖每条边角路径。

若 [SPEC.md](../../templates/to-spec/SPEC.md) 中已有 **Seam 分析** 章节，直接以此为 input 执行循环；若无，先向 AI 确认 seam 后再开始循环。

## 抗模式

看 [tests.md](tests.md) 获取完整代码示例。

- **实现耦合（implementation-coupled）** — Mock 内部协作者、测试私有方法、通过旁路验证（查数据库而非走接口）。特征：重构时测试失败但行为未变。
- **同义反复（tautological）** — 断言的计算方式与代码一致（`expect(add(a, b)).toBe(a + b)`），测试通过任何输入。预期值必须来自独立来源 —— 已知正确字面量、手动推算示例、规格说明。
- **水平切片（horizontal slicing）** — 先写完所有测试再实现。批量测试验证的是**想象中**的行为而非用户可见行为，测试对真实变更不敏感。应垂直切片 —— 一个测试 → 一个实现 → 重复，每个测试都是**示踪弹**，响应上一轮循环带来的真实认知。

## 循环纪律

- **红在前绿在后。** 先写失败测试，再写刚好够通过的代码。不要预判未来测试或添加推测性功能。
- **一次一片。** 一个 seam、一个测试、一次最小实现 —— 每轮。
- **重构不是循环的一部分。** 重构属于 review 阶段（见 `code-review` 技能），而非红→绿实现循环。