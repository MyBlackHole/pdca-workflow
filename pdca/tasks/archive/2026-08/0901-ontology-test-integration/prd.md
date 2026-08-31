# 优化本体与任务拆分、测试案例的融合

## 背景

当前本体在任务拆分与测试案例辅助两个方向的融合存在以下缺口：
1. **泛化信号残留**：大量 `ontology/domain/` 节点的 `attributes.testable_signal` 仍含"由领域实践与测试验证"等不可派生描述（T0461 已识别 178 信号中 125 个为泛化）。
2. **测试用例自动化派生断层**：`testable-signal-to-test-derivation` 已定义三种派生模式（属性断言/契约测试/收敛验证），但 `skill-testing-strategy.md` 未引用该模式，缺乏从 `testable_signal` 到测试用例的自动生成链路。
3. **任务拆分中的本体门禁偏弱**：`skill-to-tickets.md` 的本体一致性预检仅"提示不阻断"，关系树驱动拆分为可选顾问式步骤。

## 范围

- **Phase 1 (research)**：量化 `ontology/domain/` 层泛化信号残留比例，梳理可精化信号清单；评估 `testable-signal-to-test-derivation` 三模式在现有 domain 节点上的可落地性。
- **Phase 2 (development)**：精化泛化信号为可执行断言；打通 `testable_signal` → 测试用例的自动化派生链路；强化任务拆分中的本体门禁（可选，后续迭代）。

## 目标本体

- `ontology/domain/` 层（泛化信号最集中，`tool-production-readiness` 为精化正例）

## 验收标准

- [ ] AC-1：产出 `ontology/domain/` 层泛化信号清单，精化后信号均含"动词+对象+判定"结构
- [ ] AC-2：`testable-signal-to-test-derivation` 三模式在至少 1 个 domain 节点上可运行验证
- [ ] AC-3：`ontology-validate` 通过且 `ontology_graph` 0 islands

## 关联本体节点

```
ontology:pattern/testable-signal-to-test-derivation
ontology:domain/tool-production-readiness
ontology:concept/pdca-task
```

## 拆分映射

- 泛化信号清理 → `ontology/domain/` 节点精化
- 自动化派生链路 → `ontology/pattern/testable-signal-to-test-derivation` 落地验证