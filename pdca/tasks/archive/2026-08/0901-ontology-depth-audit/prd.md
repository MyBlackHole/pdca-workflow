# 扩展本体深度审计与结算门禁及研究技能强化

## 背景

T0468 已完成以下工作：
- 77 个无信号文件补充 `testable_signal`，泛化信号残留保持 0%
- `skill-testing-strategy.md` 引用 `testable-signal-to-test-derivation` 三模式
- `ontology-clash-check.py` 升级为阻断门禁

但仍有遗留迭代方向：
1. **`check-ontology-reference-depth.py` 仅为可选深度审计**（非硬门禁），需评估是否升级为硬门禁
2. **精化后的信号未注册为 `check-research-ontology-settlement` 门禁的校验条件**
3. **`skill-research.md` 的 `## 本体沉淀决策` 未强化三模式引用**

## 范围

- **Phase 1 (research)**：评估 `check-ontology-reference-depth.py` 当前行为与升级方案；梳理 `check-research-ontology-settlement` 的校验条件；评估 `skill-research.md` 本体沉淀决策的强化方案。
- **Phase 2 (development)**：扩展深度审计为硬门禁（可选）；注册精化信号为结算门禁校验条件；在 `skill-research.md` 强化三模式引用。

## 目标本体

- `scripts/` 层（深度审计脚本）
- `ontology/domain/` 层（结算门禁校验）
- `ontology/domain/skill-research.md`（本体沉淀决策）

## 验收标准

- [ ] AC-1：`check-ontology-reference-depth.py` 完成深度审计扩展，`ontology-validate.py` 通过
- [ ] AC-2：精化后的 `testable_signal` 注册为 `check-research-ontology-settlement` 门禁校验条件，`ontology-validate.py` 通过
- [ ] AC-3：`skill-research.md` 的 `## 本体沉淀决策` 强化三模式引用，`ontology-validate.py` 通过且 `ontology_graph` 0 islands

## 关联本体节点

```
ontology:domain/skill-research
ontology:pattern/testable-signal-to-test-derivation
ontology:concept/pdca-task
```

## 拆分映射

- 深度审计扩展 → `scripts/check-ontology-reference-depth.py`
- 结算门禁注册 → `check-research-ontology-settlement.py` + `ontology/domain/`
- 研究技能强化 → `skill-research.md`