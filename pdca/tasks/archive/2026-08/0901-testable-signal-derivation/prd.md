# 建立 testable_signal 到测试用例派生机制

## 背景

当前本体 178 个 attributes 中 53 具体/125 泛化（`由领域实践与测试验证`），泛化全部集中在 `domain` 层（122个知识沉淀），`concept/pattern/principle/pitfall/fact` 已 92-100% 具体化。GAP-01 的本质不是链路缺口，是信号质量问题——70% 信号不可直接派生断言。本任务不批量精化 122 个泛化，而是建立"新增时强制具体 + 示范派生"的机制。

## 目标

建立 `testable_signal → 测试用例` 的可复用派生机制，使本体真正驱动测试生成，并为后续新增节点提供约束。

## 验收标准

- [ ] AC-1 新增 `ontology/pattern/testable-signal-to-test-derivation.md`（`type: pattern`，`specializes: pattern`，`guides: ontology-asset`），描述 3 种派生模式（属性断言/契约测试/收敛验证）与示例
- [ ] AC-2 扩展 `ontology/domain/skill-ontology-check.md`，在门禁步骤中增加"新增 KnowledgeArtifact 的 attributes.testable_signal 不得为泛化描述"的校验指引（与 `ontology-validate` AC-4 衔接）
- [ ] AC-3 选取 2 个现有泛化 `domain` 节点做示范精化（将 `由领域实践与测试验证` 改为具体信号，如"检查 PRD 是否含可验证的验收标准"等），验证派生可行性
- [ ] AC-4 `ontology-validate.py --ontology-dir ontology` 通过且 `ontology_graph --format summary` islands:0

## 非目标

- 不批量精化全部 122 个泛化信号（投入大、收益递减）
- 不改动 `ontology-validate.py` 的校验逻辑本身（仅 skill 文档指引）

## 关联本体节点

```
ontology:pattern/testable-signal-to-test-derivation
ontology:domain/skill-ontology-check
ontology:concept/ontology-validate
ontology:concept/ontology-asset
```

## 风险

- 示范精化的 2 个节点需选代表性强的，避免"为改而改"
- pattern 节点的 `guides` 需指向合法的 DomainEntity/Process 类，避免 AC-6 告警
