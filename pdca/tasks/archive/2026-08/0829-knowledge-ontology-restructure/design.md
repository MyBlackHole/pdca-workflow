# 设计文档 — 知识表达按本体论重构

## 1. 目录结构

```
ontology/
  README.md                  # SSOT：类型词汇、关系语义、属性结构、组合规则
  <type>/<slug>.md           # 本体节点（type ∈ 受控词汇，且 == 父目录名）
  domain/<entity>.md         # 领域实体定义（如 tls-session、backup）
records/<record>/...         # PDCA 任务元数据不动；evidence/ 与 experience.md 迁出至 ontology/
```

**目录即真理**：节点的 `ontology_type` 由所在 `<type>/` 目录名决定，不在 manifest 冗余存储。

## 2. 本体节点 frontmatter schema（pdca.asset/v1 扩展）

```yaml
---
schema: pdca.asset/v1
id: ontology:<type>/<slug>
type: <type>                     # 必须 == 父目录名
layer: <Evidence|Experience|Knowledge|Skill>
summary: <一句话>
tags: [...]
attributes:                     # 知识权威来源的可测点
  - name: <属性名>
    desc: <描述>
    constraint: <约束/取值>
    testable_signal: <可测信号，供派生测试>
relations:
  specializes: [<ontology id>]  # is-a 泛化/特化（构成层次树）
  instance_of: [<ontology id>]  # 实例化
  composed_of: [<ontology id>]  # 组合（多实体表达一个实体）
  part_of: [<ontology id>]
  depends_on: [<ontology id>]
  relates_to: [<ontology id>]
domain: [<ontology/domain id>] # 领域实体引用（md 链接）
source_ids: [...]               # 来源 record / 经验
confidence: <high|medium|low>
status: active
---
```

## 3. 关系词汇表语义

- `specializes`：A specializes B ⇒ A 是 B 的特化；构成 is-a 层次树；**必须无环**。
- `instance_of`：A instance_of B ⇒ A 是 B 的实例。
- `composed_of` / `part_of`：高层实体由多个子实体组合表达；子实体属性可聚合到高层。
- `depends_on`：实现/理解依赖。
- `relates_to`：弱相关（无层次语义）。

## 4. attributes 结构

每项含 `name` / `desc` / `constraint` / `testable_signal`；`testable_signal` 描述如何验证该属性（如"调用 X 返回 Y"），供派生测试用例。`ontology-validate` 校验每个 attribute 都有回链本体的测试覆盖。

## 5. manifest.jsonl 扩展

每行保留既有字段（`version`/`revision`/`at`/`knowledge`/`knowledge_digest`/`source_record`/`source_digest`/`reason`），新增派生索引：`ontology_type`（由路径推导）、`specializes`、`domain`、`entity_refs`、`attributes_keys`。

## 6. ontology-validate.py 设计

- 扫描 `ontology/**/*.md`
- 断言：`type` == 父目录名；`relations`/`domain` 引用存在；`specializes`/`instance_of`/`composed_of`/`part_of` 构成 **DAG 无环**
- `attributes` 结构合法；每个 `attribute` 须有回链本 `id` 的测试（grep 测试文件）
- 输出 errors 列表，退出码 0/1
- 自测：用 `scripts/tests/` 下确定性夹具（合法/非法样例）

## 7. ontology-check skill 设计

- `skills/ontology-check/SKILL.md` 描述写入门禁：新资产须含合法 `type`、`relations` 引用存在、`attributes` 有测试覆盖
- 调用 `ontology-validate.py` 单文件模式
- 与 `register-evidence` 同级

## 8. 归纳工作流（AI）

Do 阶段处理某域时：列出候选具体实例 → AI 分析共性 → 创建抽象节点 A → 使实例 `specializes` A → 运行 `ontology-validate` 保证无环。

## 9. record identity 保持（见 ADR-0030）

物理归并后：被迁 `evidence`/`experience` 在新位置 frontmatter 保留 `source_task: <record>`；`task.json` 的 `meta.record` 指向新 `ontology/` 路径；保留 `records/<record>/` 空壳 + redirect 说明，保证历史引用不失效。

## 10. 迁移设计

- **试点 tls**：11 个文件 + 相关 records 的 evidence/experience 归入 `ontology/pattern|pitfall|decision|fact|concept` 等；建立 `domain/tls-session.md` 等；演示 AC-3/AC-4/AC-5。
- **全量**：其余域按同法迁移；manifest 全量重写索引。
- **不迁移**：`flows/`、`skills/`、`task.json` 等机制层。

## 11. SSOT（ontology/README.md 草案）

Do 阶段落地，含：类型受控词汇（`concept`/`principle`/`pattern`/`pitfall`/`decision`/`fact`/`process`，可扩展）、关系词汇表、attributes 结构、组合规则、目录即真理约定。
