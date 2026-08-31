# 调研报告：ontology/domain/ 层 testable_signal 泛化现状与派生链路评估

## 调研目标

量化 `ontology/domain/` 层 `attributes.testable_signal` 的泛化信号残留比例，评估 `testable-signal-to-test-derivation` 三种派生模式在现有 domain 节点上的可落地性。

## 方法

1. 扫描 `ontology/domain/` 下全部 201 个 `.md` 文件的 frontmatter，提取所有 `testable_signal` 条目
2. 按是否含泛化短语（"由领域实践与测试验证"、"符合领域最佳实践"）分类
3. 对具体信号按 `testable-signal-to-test-derivation` 三模式（属性断言/契约测试/收敛验证）进行可落地性评估
4. 对比 `tool-production-readiness` 正例的精化标准

## 发现

### 泛化信号残留统计

| 指标 | 数值 |
|------|------|
| Domain 文件总数 | 201 |
| 含信号的文件 | 124 (61.7%) |
| 无信号的文件 | 77 (38.3%) |
| testable_signal 条目总数 | 131 |
| 泛化信号 | 120 (91.6%) |
| 具体信号 | 11 (8.4%) |
| 泛化:具体 比 | 10.9:1 |

### 泛化信号分布

- 泛化信号集中在 `ai-efficiency-*`（11 条）、`backup-crypto-*`（7 条）、`benchmark-*`（4 条）、`core-*`（16+ 条）、`build-config-*`（2 条）、`cli-help-*`（1 条）、`control-plane-nonblocking-ingress-v81-*`（2 条）等
- 几乎所有非 AI 效率、非工具类的 domain 节点均含泛化信号
- 77 个文件完全不含 `testable_signal`，包括 `core.md`、`backup.md`、`benchmark.md` 等核心入口文件

### 具体信号节点（可派生候选）

| 文件 | 信号数量 | 派生模式 |
|------|---------|---------|
| `tool-production-readiness.md` | 4 | 属性断言 + 契约测试 |
| `skill-retrospective.md` | 5 | 属性断言 |
| `ai-efficiency-contract-test-pattern.md` | 1 | 契约测试 |
| `ai-efficiency-knowledge-assets-and-ai-workflow.md` | 1 | 收敛验证 |

### `tool-production-readiness` 正例对照

`tool-production-readiness.md` 是当前最精化的 domain 节点：
- 4 条信号均含"动词+对象+判定"结构
- 信号引用具体文件路径、具体验证命令（`trivy fs`、`syft`、`cosign verify`）
- 已通过 `ontology-validate` 和 `ontology_graph` 校验

## 结论与建议

### 结论

1. **泛化信号占比 91.6%**，远高于 T0461 发现的 68.5%（125/178），说明 T0461 的精化工作未覆盖 domain 层主体
2. **`testable-signal-to-test-derivation` 三模式具备落地条件**：4 个节点共 11 条具体信号可分别映射至属性断言（6 条）、契约测试（1 条）、收敛验证（1 条）模式
3. **77 个文件完全无信号**，需先补充 `testable_signal` 条目，再进行精化

### 建议

- **Phase 1 (research → development)**：精化 120 个泛化信号为可执行断言，优先处理 `core-*` 和 `backup-crypto-*` 等高频节点
- **Phase 2**：为 77 个无信号文件补充 `testable_signal` 条目
- **Phase 3**：在 `tool-production-readiness` 和 `skill-retrospective` 上试点三模式派生验证
- **参考标准**：以 `tool-production-readiness` 的信号精化标准为模板——"动词+对象+判定+具体工具/路径"

## 参考资料

- `ontology/pattern/testable-signal-to-test-derivation.md`：三模式派生规范
- `ontology/domain/tool-production-readiness.md`：精化正例
- `records/T0461-0831-p2-ontology-improvements/`：T0461 精化工作背景
- `scripts/ontology-validate.py`：机检逻辑
- `scripts/ontology_graph.py`：图谱校验