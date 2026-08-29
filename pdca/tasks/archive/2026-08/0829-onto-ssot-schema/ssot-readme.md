# 本体 SSOT（Single Source of Truth）

本文件定义 PDCA 知识库本体化的统一词汇表、关系语义、属性结构与组合规则。所有 `ontology/` 下的资产必须遵守。

## 1. 目的与三合一用途

本体是知识的**语义引擎**，承担三重职责：

1. **知识权威来源**：本体描述实体"是什么样子"（结构化 `attributes`/`features`），其所有描述信息都是可测试点（single source of truth）。
2. **验证契约**：每个属性/特征都是可测点，派生测试用例验证实现是否匹配本体；测试回链本体 `id`。
3. **关系树驱动任务分解**：复杂实体由多本体 + 多层父子（`specializes`）关系构成关系树，据此自底向上拆分任务，每个本体的实现可独立收敛（WBS）。

## 2. 目录约定（目录即真理）

```
ontology/
  README.md                  # 本文件（SSOT）
  <type>/<slug>.md           # 本体节点；type 必须 == 父目录名
  domain/<entity>.md         # 领域实体定义（如 tls-session、backup）
```

- `ontology_type` 由所在 `<type>/` 目录名决定，不在 frontmatter 冗余存储（杜绝漂移）。
- 层次由 `specializes`/`instance_of` 关系表达，父子节点不必同目录。

## 3. 类型受控词汇（起点，可扩展）

`concept` / `principle` / `pattern` / `pitfall` / `decision` / `fact` / `process`

- 新增类型须在此登记并说明理由（开放但不失控）。
- 每个节点可带 `also_type`（辅助类型）表达跨类归属。

## 4. 关系词汇表

| 关系 | 语义 | 约束 |
|------|------|------|
| `specializes` | A specializes B ⇒ A 是 B 的特化（is-a） | 构成层次树，无环 |
| `instance_of` | A instance_of B ⇒ A 是 B 的实例 | — |
| `composed_of` | 高层实体由多个子实体组合表达 | 子实体属性可聚合到高层 |
| `part_of` | 反组合关系 | — |
| `depends_on` | 实现/理解依赖 | — |
| `relates_to` | 弱相关（无层次语义） | — |

## 5. attributes 结构（属性即测试点）

每个 attribute 项：

```yaml
attributes:
  - name: <属性名>
    desc: <描述>
    constraint: <约束/取值范围>
    testable_signal: <可测信号，描述如何验证该属性，供派生测试>
```

- `testable_signal` 是派生测试用例的源头；`ontology-validate` 校验"每个 attribute 都有回链本体的测试覆盖"。

## 6. 组合规则

- `composed_of` 多个子实体时，高层实体的有效属性 = 子实体 `attributes` 的聚合（去重后合并）。
- 归纳（自底向上）：AI 从具体实例 A1/A2/A3 分析共性，创建抽象 A，使实例 `specializes` A；`ontology-validate` 保证关系无环。

## 7. 与四层模型关系

- `layer` 字段（Evidence/Experience/Knowledge/Skill）保留资产来源层语义；本体重构跨四层物理归并（ADR-0030），但 `layer` 值不变。
- `records/*/evidence/`、`experience.md` 物理迁入 `ontology/`，新位置 frontmatter 保留 `source_task` 回链。

## 8. 门禁

- 新资产写入须经 `ontology-check` skill：合法 `type`、关系/领域引用非空悬、`attributes` 有测试覆盖。
- `ontology-validate.py` 校验：type==目录名、引用存在、关系无环、属性→测试覆盖。
