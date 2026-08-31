# 调研报告：扩展本体深度审计与结算门禁及研究技能强化

## 调研目标

1. 评估 `check-ontology-reference-depth.py` 当前状态与扩展方案
2. 梳理 `check-research-ontology-settlement.py` 的校验条件与精化信号注册方案
3. 评估 `skill-research.md` 的 `## 本体沉淀决策` 强化方案

## 方法

1. 检查 `scripts/` 下是否存在 `check-ontology-reference-depth.py`
2. 阅读 `check-research-ontology-settlement.py` 的完整逻辑
3. 阅读 `skill-research.md` 的 `## 本体沉淀决策` 章节

## 发现

### 深度审计脚本

`check-ontology-reference-depth.py` **不存在**。T0467 结论中建议"可补充 `check-ontology-reference-depth.py` 的可选深度审计（非硬门禁）"，但尚未创建。

### 结算门禁校验

`check-research-ontology-settlement.py` 存在，当前校验：
- conclusion.md 含 `## 本体沉淀` 章节
- 显式声明 `ontology:` 或 `records-only`
- `task.json#meta.disposition.reason` 含对应关键词
- 若决策为 `ontology`，至少一个本体文件引用该 record

**缺口**：未校验精化后的 `testable_signal` 是否满足 `testable-signal-to-test-derivation` 三模式的"动词+对象+判定"结构。

### 研究技能本体沉淀

`skill-research.md` 的 `## 本体沉淀决策（Act 门禁）` 章节存在，但未引用 `testable-signal-to-test-derivation` 三模式。精化后的信号应作为本体沉淀的校验条件之一。

## 结论与建议

1. **创建 `check-ontology-reference-depth.py`**：评估实例到本体的链路深度，按 `ontology-modular-reference.md` 决策树校验
2. **更新 `check-research-ontology-settlement.py`**：增加 `testable_signal` 精化校验，确保信号不含泛化短语
3. **更新 `skill-research.md`**：在 `## 本体沉淀决策` 中引用三模式，强化信号精化要求

## 参考资料

- `ontology/pattern/ontology-modular-reference.md`：链路深度决策树
- `scripts/check-research-ontology-settlement.py`：当前结算门禁逻辑
- `ontology/domain/skill-research.md`：本体沉淀决策章节
- `ontology/pattern/testable-signal-to-test-derivation.md`：三模式派生规范
