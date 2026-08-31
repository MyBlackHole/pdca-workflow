# 本体深度审计与结算门禁及研究技能强化设计（T0469）

> 决策：创建 check-ontology-reference-depth.py，更新 check-research-ontology-settlement.py 校验 testable_signal，强化 skill-research.md 本体沉淀决策。

## 1. 深度审计脚本

创建 `scripts/check-ontology-reference-depth.py`：
- 校验 ontology_graph 无 islands
- 检查单任务本体引用数通常 ≤3
- 扇出而非串联

## 2. 结算门禁更新

更新 `scripts/check-research-ontology-settlement.py`：
- 新增 `testable_signal` 精化校验
- 检测泛化短语（"由领域实践与测试验证"、"符合领域最佳实践"）
- 信号须符合 testable-signal-to-test-derivation 三模式

## 3. 研究技能强化

更新 `skill-research.md` 的 `## 本体沉淀决策`：
- `attributes[].testable_signal` 须符合三模式结构
- 校验 `testable_signal` 不含泛化短语

## 4. 验证方案

- AC-1: check-ontology-reference-depth.py 完成，ontology-validate 通过
- AC-2: check-research-ontology-settlement.py 校验 testable_signal，ontology-validate 通过
- AC-3: skill-research.md 强化三模式引用，ontology-validate 通过且 ontology_graph 0 islands
