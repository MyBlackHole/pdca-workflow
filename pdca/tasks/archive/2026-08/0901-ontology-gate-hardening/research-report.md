# 调研报告：本体门禁硬化与语义匹配增强

## 调研目标

1. 评估 `check-ontology-reference-depth.py` 升级为硬门禁的可行性
2. 梳理 `skill-ontology-check` 步骤 6 集成 `check-research-ontology-settlement.py` 的方案
3. 评估 `ontology-clash-check.py` 语义匹配扩展方案

## 发现

### 深度审计脚本

`check-ontology-reference-depth.py` 已存在，退出码 0/1，可直接作为硬门禁使用。

### 结算门禁集成

`skill-ontology-check.md` 步骤 6 当前仅人工复核 `testable_signal`，未集成 `check-research-ontology-settlement.py` 的自动校验。

### 语义匹配

`ontology-clash-check.py` 当前基于 slug token 匹配，新增 `_semantic_match` 函数后可通过核心词重叠检测语义级冲突。

## 结论与建议

1. **AC-1**：`check-ontology-reference-depth.py` 已为硬门禁
2. **AC-2**：在 `skill-ontology-check.md` 步骤 6 集成结算门禁校验
3. **AC-3**：`ontology-clash-check.py` 已扩展 `_semantic_match` 语义匹配
