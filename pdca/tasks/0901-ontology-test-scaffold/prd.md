# 测试派生硬化

## 背景
`testable_signal` 每 KnowledgeArtifact 必须有，但多为泛化描述，`testing-strategy` 未与本体三模式强绑定，无自动骨架。

## 目标
新增 `scripts/ontology_test_scaffold.py`，按三模式自动生成测试骨架，与 testing-strategy 文档互链。

## 功能需求
1. 工具输入本体节点 id，读取 `attributes[].testable_signal`，按 `testable-signal-to-test-derivation` 三模式分类：
   - 属性断言 -> `test_attr_*.py` 直接断言
   - 契约测试 -> `test_contract_*.py` 清单 vs 实际
   - 收敛验证 -> `test_convergence_*.py` 回链验证
2. 输出 `tests/test_<slug>.py` 骨架与 `scaffold-map.json`（信号->测试映射）
3. 更新 `ontology/domain/skill-testing-strategy.md` 增加一节与 pattern 互链

## 非功能
- 生成骨架可直接 `pytest` 收集
- 复用 `ontology-validate` 判定非空，不产生泛化信号

## 验收标准
- [ ] AC-1 三模式骨架：对给定节点（entity/domain/pattern 各一）能生成三类骨架且 `scaffold-map.json` 含动词+对象+判定
- [ ] AC-2 策略互链：`skill-testing-strategy` 文档新增与 pattern 的选择指南表格链接

## 关联本体节点
```
ontology:entity/ontology-deep-integration-test
ontology:pattern/testable-signal-to-test-derivation
ontology:domain/skill-testing-strategy
```

## 拆分映射
- 测试派生硬化 -> ontology:entity/ontology-deep-integration-test
