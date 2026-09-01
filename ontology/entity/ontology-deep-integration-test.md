---
schema: pdca.asset/v1
id: ontology:entity/ontology-deep-integration-test
type: entity
layer: Knowledge
status: active
summary: 测试派生硬化（testable_signal 三模式自动生成测试骨架，与测试策略强绑定）
relations:
  specializes:
    - ontology:concept/domain-entity
---

# 测试派生硬化

叶子实体2：打通本体到测试的自动链路。

- 依据 `ontology:pattern/testable-signal-to-test-derivation` 三模式（属性断言/契约测试/收敛验证），新增 `scripts/ontology_test_scaffold.py --node ontology:xxx`
- 输入本体节点 `attributes[].testable_signal`，输出 `tests/test_<slug>.py` 骨架与映射表
- 与 `ontology:domain/skill-testing-strategy` 强绑定：`testing-strategy` 生成测试计划时必须引用本体信号源
