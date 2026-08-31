# 本体门禁硬化与语义匹配增强

## 背景

T0469 遗留迭代方向：
1. `check-ontology-reference-depth.py` 从可选升级为硬门禁
2. `skill-ontology-check` 步骤 6 集成 `check-research-ontology-settlement.py` 的 testable_signal 校验
3. `ontology-clash-check.py` 语义匹配算法扩展

## 范围

- **Phase 1 (research)**：评估当前门禁和语义匹配现状。
- **Phase 2 (development)**：实施三项改进。

## 目标本体

- `scripts/` 层（深度审计脚本）
- `ontology/domain/` 层（结算门禁校验）
- `ontology/domain/skill-ontology-check.md`（门禁集成）

## 验收标准

- [ ] AC-1：check-ontology-reference-depth.py 从可选升级为硬门禁，ontology-validate.py 通过
- [ ] AC-2：skill-ontology-check 步骤 6 集成 check-research-ontology-settlement.py 的 testable_signal 校验，ontology-validate.py 通过
- [ ] AC-3：ontology-clash-check.py 语义匹配算法扩展，ontology-validate.py 通过且 ontology_graph 0 islands

## 关联本体节点

```
ontology:domain/skill-ontology-check
ontology:pattern/testable-signal-to-test-derivation
ontology:concept/pdca-task
```

## 拆分映射

- 深度审计硬门禁 → `scripts/check-ontology-reference-depth.py`
- 结算门禁集成 → `skill-ontology-check.md` 步骤 6
- 语义匹配扩展 → `scripts/ontology-clash-check.py`