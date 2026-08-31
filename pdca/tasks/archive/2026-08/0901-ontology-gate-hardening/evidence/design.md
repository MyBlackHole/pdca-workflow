# 本体门禁硬化与语义匹配增强设计（T0470）

## 1. 深度审计硬门禁

`check-ontology-reference-depth.py` 已为硬门禁（exit code 0/1），可直接使用。

## 2. 结算门禁集成

`skill-ontology-check.md` 步骤 6 新增：运行 `check-research-ontology-settlement.py` 校验 `testable_signal` 精化程度。

## 3. 语义匹配扩展

`ontology-clash-check.py` 新增 `_semantic_match` 函数，通过核心词重叠检测语义级冲突。

## 验证方案

- AC-1: check-ontology-reference-depth.py 为硬门禁
- AC-2: skill-ontology-check.md 步骤 6 集成结算门禁
- AC-3: ontology-clash-check.py 语义匹配扩展
