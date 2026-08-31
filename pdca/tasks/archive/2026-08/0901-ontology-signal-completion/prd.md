# 补完 domain 层 testable_signal 并打通三模式派生链路

## 背景

T0467 已完成以下工作：
- 120 个泛化信号精化为可执行断言（0% 残留）
- `testable-signal-to-test-derivation` 三模式在 4 个 domain 节点验证通过
- `ontology-validate` OK，`ontology_graph` 351 nodes / 767 edges / 0 islands

但仍有遗留缺口：
1. **77 个 domain 文件无 `testable_signal`**（38.3% 文件缺失），包括 `core.md`、`backup.md`、`benchmark.md` 等入口文件
2. **`ontology-clash-check.py` 仅"提示不阻断"**，本体一致性预检未升级为阻断门禁
3. **`skill-testing-strategy.md` 未引用 `testable-signal-to-test-derivation` 三模式**，缺乏从 `testable_signal` 到测试用例的自动生成链路

## 范围

- **Phase 1 (research)**：量化 77 个无信号文件的现状；评估三模式在 `skill-testing-strategy.md` 中的可引用性；梳理 `ontology-clash-check.py` 的升级方案。
- **Phase 2 (development)**：为 77 个文件补充 `testable_signal` 条目；将 `testable-signal-to-test-derivation` 三模式写入 `skill-testing-strategy.md`；升级 `ontology-clash-check.py` 为阻断门禁。

## 目标本体

- `ontology/domain/` 层（补信号）
- `ontology/pattern/` 层（三模式引用）
- `skill-testing-strategy.md`（链路打通）

## 验收标准

- [ ] AC-1：77 个无信号文件均补充 `testable_signal` 条目，且经 `ontology-validate.py` 校验通过
- [ ] AC-2：`skill-testing-strategy.md` 引用 `testable-signal-to-test-derivation` 三模式，且 `ontology-validate.py` 通过
- [ ] AC-3：`ontology-clash-check.py` 升级为阻断门禁，`ontology-validate.py` 通过且 `ontology_graph` 0 islands

## 关联本体节点

```
ontology:pattern/testable-signal-to-test-derivation
ontology:domain/tool-production-readiness
ontology:concept/pdca-task
```

## 拆分映射

- 补信号 → `ontology/domain/` 节点精化
- 三模式引用 → `skill-testing-strategy.md` + `ontology/pattern/`
- 门禁升级 → `ontology-clash-check.py` + `scripts/ontology-clash-check.py`