# 知识表达按本体论重构 — 规格文档

## 问题陈述

- **现状**：知识按领域主题（tls / core / pg / data-formats …）存放，共 161 个 markdown 文件，仅 31 个含 `pdca.asset/v1` frontmatter，且 knowledge/ 中混入了本应属于 Experience 层的"一次任务经验"笔记；manifest.jsonl 以 topic 为分类维度登记 192 条，无本体维度；知识间无类型化关系、无属性结构、无验证契约、无任务分解依据。
- **目标**：将知识表达从"按主题"重构为"按完整本体"，使每个保存的知识都是可层次化、可归纳抽象、属性可派生测试、关系树可驱动任务分解的本体节点。
- **差距**：缺少本体类型 / 关系 / 属性词汇表（SSOT）；缺少关系与属性的机器可读表达；缺少一致性校验与写入门禁；存量知识未本体化。

## 解决方案

建立以 `ontology/` 为根的**轻量知识图谱**（完整本体）：

- 每个本体节点 = 一个 `ontology/<type>/<slug>.md`，frontmatter 声明唯一 `id`、`type`、`layer`、**结构化 `attributes`**、**类型化关系**。
- 类型化关系：`specializes`（泛化/特化 is-a）、`instance_of`（实例化）、`composed_of`/`part_of`（组合）、`depends_on`、`relates_to`；领域实体用 md 链接引用 `ontology/domain/<entity>.md`。
- **三合一用途**：
  1. **知识权威来源**：本体描述实体"是什么样子"，其所有描述信息都是可测试点（single source of truth）。
  2. **验证契约**：每个属性/特征都是可测点，派生测试用例验证实现是否匹配本体，测试回链本体 `id`。
  3. **关系树驱动任务分解**：复杂实体由多本体 + 多层父子关系构成关系树，据此自底向上拆分任务，每个本体实现可独立收敛，从叶子逐层实现到根（WBS）。

## 用户故事

1. 作为 AI 代理，我想按本体（类型/领域/关系）检索与复用知识，以便新任务快速定位相关概念、模式、反模式。
2. 作为维护者，我想用本体 `attributes` 派生测试来验证实现正确性，以便实现不偏离权威定义。
3. 作为规划者，我想用本体关系树自底向上拆分任务，以便每个本体的实现可独立收敛。
4. 作为知识作者，我想新写知识经门禁校验后按本体登记，以便知识库不退化。

## 实现决策

- **目录**：`ontology/<type>/<slug>.md` + `ontology/domain/<entity>.md`；**目录即真理**（`type` == 目录名），层次由 `specializes` 关系表达（父子不必同目录）。
- **frontmatter schema（pdca.asset/v1 扩展）**：`id`、`type`、`layer`、`summary`、`tags`、`attributes[{name, desc, constraint, testable_signal}]`、`relations{specializes, instance_of, composed_of, part_of, depends_on, relates_to}`、`domain`、`source_ids`、`confidence`、`status`。
- **类型受控词汇起点（可扩展）**：`concept` / `principle` / `pattern` / `pitfall` / `decision` / `fact` / `process`。
- **关系词汇表**：`specializes`（is-a 泛化/特化）、`instance_of`（实例化）、`composed_of`/`part_of`（组合/聚合）、`depends_on`、`relates_to`。
- **索引**：`manifest.jsonl` 保留来源边（`source_record`/`digest`/`revision`），并派生 `ontology_type`（由路径推导）、`specializes`、`domain`、`entity_refs`、`attributes` 索引字段，供按本体检索/注入。
- **校验**：`scripts/ontology-validate.py` 断言：① `type` == 父目录名；② 关系/领域引用非空悬；③ 关系无环；④ `attributes` 结构化合法且"声明属性都有对应测试覆盖"。
- **门禁**：`skills/ontology-check`（与 register-evidence 同级）作为写入门禁，缺合法 `type` / 悬空引用 / 属性无测试覆盖则拒绝登记。
- **归纳**：AI 在 Do 阶段从具体实例 A1/A2/A3 分析共性、创建抽象 A、使实例引用 A；`ontology-validate` 保证无环。
- **record identity 保持**：物理归并后，被迁出的 `evidence`/`experience` 在新位置 frontmatter 保留 `source_task` 回链；`meta.record` 指向新 `ontology/` 路径或保留映射表（具体方案见 ADR）。
- 详细设计见 `design.md`；词汇表 SSOT 落地为 `ontology/README.md`（Do 阶段创建）。

## 测试决策

- 本任务交付 `ontology-validate.py`，其逻辑用确定性夹具自测（可重复、不依赖模型）。
- 本体 `attributes → 测试覆盖` 由 `ontology-validate` 校验（属性须有回链本体的测试）。
- 迁移不破坏检索/P5 注入：用 grep 验证旧主题路径引用已更新为本体路径。

## 验收标准

- [ ] AC-1: 运行 `python3 scripts/ontology-validate.py --all` 退出码为 0；所有 ontology 节点 frontmatter 含合法 `id`、`type`==目录名、`attributes` 结构化合法、关系引用存在且无环
- [ ] AC-2: 存在 `ontology/README.md`（SSOT）定义类型受控词汇起点、关系词汇表、attributes 字段结构、组合规则
- [ ] AC-3: 试点 tls 域至少 1 个抽象节点 A 由 ≥2 个实例 A1/A2 经 `specializes` 引用构成（演示归纳自底向上）
- [ ] AC-4: 至少 1 个本体节点的 `attributes` 作为验证契约，存在回链该 `id` 的测试，`ontology-validate` 报告属性覆盖率 100%
- [ ] AC-5: 至少 1 个复杂实体 `composed_of` ≥2 个子实体，子实体属性可聚合展示
- [ ] AC-6: `manifest.jsonl` 每条迁移资产含派生 `ontology_type`（由路径推导）、`specializes`、`domain`、`entity_refs`、`attributes` 索引
- [ ] AC-7: 新写入资产经 `ontology-check` 门禁；缺合法 `type` / 悬空引用 / 属性无测试覆盖则拒绝登记
- [ ] AC-8: 试点 tls 的 11 个文件全量归并至 `ontology/` 后，检索与 P5 注入逻辑不受影响（grep 验证旧引用已更新）
- [ ] AC-9: 物理归并后 record identity 保持——被迁 `evidence`/`experience` 在新位置可经 `source_task` 追溯到原 task（ADR 方案落地）
- [ ] AC-10: 提供关系树查询能力（给定根节点列出叶子→根路径），可演示自底向上任务拆分

## 范围外

- 不改动 `flows/`、`skills/`（PDCA 机制层）与 `task.json` 等任务元数据
- 不引入 OWL/RDF 形式本体与推理机
- 不迁移 `records/` 下除 `evidence/`、`experience.md` 外的其他文件
- 不在试点验证前执行一次性全量迁移

## 备注

- 本任务 `scenario_type=design`，但交付含可执行脚本（`ontology-validate.py`、`ontology-check` skill），其自测在 Do 阶段完成。
- 关键不可逆决策"全部物理归并"写入 ADR（见 `design.md` 与 `docs/adr/`）。
- 迁移策略：试点 `tls` 域先行，验证检索/注入/校验/门禁不受影响后，再全量推广至其余域。
