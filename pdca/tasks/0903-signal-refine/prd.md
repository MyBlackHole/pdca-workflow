# 存量信号去泛化：全量精化与三模式可生成

## 背景
存量 `ontology/**/*.md` 中仍有 `由领域实践与测试验证` 等泛化 `testable_signal`，无法按 `ontology:pattern/testable-signal-to-test-derivation` 三模式派生可执行断言。

## 目标
全量泛化清零，抽样可经 `ontology_test_scaffold` 生成三桩且 pytest 可收集。

## 功能需求
1. 扫描 `grep -rn "由领域实践与测试验证" ontology` 全量识别泛化节点
2. 按三模式精化为含动词+对象+判定+脚本的信号（属性断言/契约测试/收敛验证）
3. 抽样10节点 `python3 scripts/ontology_test_scaffold.py --node ontology:xxx --out /tmp/` 验证产出

## 非功能需求
- 不新增独立清单节点，清单透传按 `ontology-modular-reference:checklist_propagation`
- 单节点 `attributes` 通常3条以内，链路≤3

## 验收标准
- [ ] AC-1 grep 泛化 `wc -l == 0` 且 `ontology-validate` 0 issues
- [ ] AC-2 抽样10节点均产 `test_*.py` 与 `scaffold-map.json` 且 `pytest --collect-only` 可收集 且 `graph islands:0`


## 关联本体节点
```
ontology:pattern/testable-signal-to-test-derivation
ontology:concept/ontology-rule-attr-testable
ontology:domain/skill-ontology-check
```

## 风险与对策
- 风险：精化引入引用空悬。对策：`ontology-validate` AC-2 拦，`relations` 强引用必存在
