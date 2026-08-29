# 本体 SSOT（Single Source of Truth）v3 — 实体本体模型

> 演进注记：本 v3 取代 T0400（0829-onto-ssot-schema）归档的 taxonomy 式 v1 SSOT。v1 把知识形态（pattern/principle…）直接作为 `type` 顶层分类，实为分类法（taxonomy）；v3 按本体工程方法论（Gruber 五原则、Ontology 101、Palantir "Model reality not systems"、Schema-vs-Ontology 区分）修正为**实体类型层次 + 属性 + 关系图**。本文件为语义主干（ontology），`pdca.asset/v1` frontmatter 为其编码（schema），各 md 文件 + 其 relations 构成知识图谱（KG）。

## 1. 目的与三合一用途

本体是知识的**语义引擎**，承担三重职责：

1. **知识权威来源**：本体描述实体"是什么样子"（结构化 `attributes`），其所有描述信息都是可测试点（single source of truth）。
2. **验证契约**：每个属性都是可测点，派生测试用例验证实现是否匹配本体；测试回链本体 `id`。
3. **关系树驱动任务分解**：复杂实体由多实体 + 多层 `specializes` 关系构成关系树，据此自底向上拆分任务，每个实体实现可独立收敛（WBS）。

## 2. 目录约定（目录即真理）

```
ontology/
  README.md                       # 本文件（SSOT）
  <type>/<slug>.md                # 本体节点；type 必须 == 父目录名
  entity/<entity>.md              # 领域实体定义（如 tls-session、mtls-handshake）
  pattern/<slug>.md               # 知识形态：可复用结构/方法
  principle/<slug>.md             # 知识形态：必须遵守的准则
  pitfall/<slug>.md               # 知识形态：易错点/反模式
  fact/<slug>.md                  # 知识形态：稳定事实/调查状态
  decision/<slug>.md              # 知识形态：具体决定（含理由）
  concept/<slug>.md               # 抽象概念定义
  process/<slug>.md               # 执行流程/过程（如 code-review-process）
  role/<slug>.md                  # 角色
```

- `type` 字段由所在 `<type>/` 目录名决定；frontmatter 保留 `type`（便于检索），其值**必须 == 父目录名**，由 `ontology-validate` 校验（目录为权威源，字段为镜像）。
- 层次与挂接由 `specializes` / `composed_of` / `configured_by` / `guides` / `relates_to` 关系表达，节点不必同目录（平铺目录 + 关系表达层次，grill Q13 选定）。

## 3. 实体类型层次（specializes = is-a / kind-of）

```
Entity (root)
├─ DomainEntity ── specializes ──> Entity            [真实世界实体分组]
│   ├─ TLSSession        (composed_of: MTLSHandshake, X509Certificate; configured_by: TLSConfiguration)
│   ├─ MTLSHandshake     (composed_of: X509Certificate)
│   ├─ X509Certificate
│   ├─ TLSConfiguration
│   ├─ TLSTestHarness
│   └─ ExecStdinPump
├─ Process ── specializes ──> Entity
│   └─ CodeReviewProcess
└─ KnowledgeArtifact ── specializes ──> Entity      [知识实体]
    ├─ Pattern   (knowledge_form=pattern)
    ├─ Principle (knowledge_form=principle)
    ├─ Pitfall   (knowledge_form=pitfall)
    ├─ Fact      (knowledge_form=fact)
    └─ Decision  (knowledge_form=decision)
```

- **md 文件 = KnowledgeArtifact / DomainEntity / Process 的实例**，通过 `specializes` 指向上述类（实例 → 类）。绝不可把单篇实例当作类（Ontology 101 警告：single X 不是 all X 的子类）。
  - **类节点类型约定**：知识**类**节点（`Pattern`/`Principle`/`Pitfall`/`Fact`/`Decision`）存放于 `concept/` 目录、使用 `type: concept`，其 `id` 为 `ontology:pattern` 等；知识**实例**则按形态存放于 `pattern/`、`principle/` 等目录、使用对应 `type`，并 `specializes` 指向类节点。类节点刻意用 `concept` 类型，以豁免 AC-5（知识实例须有 `guides`/`relates_to`）对"类"本身的约束——类是概念而非知识实例。
  - 知识形态（`knowledge_form`：pattern/principle/pitfall/fact/decision）不另设为独立属性，而由实例的 `type` 字段及其所在目录直接承载——`type` 即形态的一手事实来源，避免冗余字段与校验漂移（README §3 类型树中标注的 `knowledge_form=*` 仅为语义提示，非存储字段）。
- 新增领域实体：加 `DomainEntity` / `Process` 子类（在 README §3 登记）；新增知识形态：加 `KnowledgeArtifact` 子类（开放但不失控）。
- `specializes` 必须形成以 `Entity` 为根的有向无环树。

## 4. 类型受控词汇（type 值）

`domain` / `entity` / `concept` / `process` / `role` / `pattern` / `principle` / `pitfall` / `fact` / `decision`

- 领域实体实例目录用 `entity/`（或 `domain/` 作同义分组）；知识形态实例按形态入 `pattern/` / `principle/` / `pitfall/` / `fact/` / `decision/`。
- 新增类型须在此登记并说明理由。每个节点可带 `also_type`（辅助类型）表达跨类归属。

## 5. 关系词汇表（带 domain / range）

| 关系 | 语义 | domain（主体） | range（客体） |
|------|------|---------------|---------------|
| `specializes` | A specializes B ⇒ A 是 B 的特化（is-a） | 任意实体/实例 | 父类（Entity 谱系） |
| `composed_of` | 整体由部分实体组合（真实部分-整体） | 整体实体 | 部分实体 |
| `configured_by` | 实体由某配置参数化 | 实体 | TLSConfiguration 节点（`ontology:entity/tls-configuration`） |
| `guides` | 知识指导某类实体/过程 | KnowledgeArtifact 实例 | DomainEntity / Process 类 |
| `relates_to` | 弱相关（跨文档关联，非 is-a 非组合） | 任意 | 任意 |
| `instance_of` / `part_of` | 可选/派生 | — | 分别由 `specializes` / `composed_of` 反向派生，不强制存储 |

- `guides` 是知识挂接领域实体的核心关系；每 KnowledgeArtifact 实例应至少 1 条 `guides`（或 `relates_to`），保证关系丰富度（防 taxonomy 退化）。

## 6. attributes 结构（属性即测试点，防 taxonomy 退化）

每个 KnowledgeArtifact 实例**必须**有结构化 `attributes`（frontmatter 字段或正文 `## 适用`/`## 约束`/`## 验收` 固定章节映射）：

```yaml
attributes:
  - name: <属性名>
    desc: <描述>
    constraint: <约束/取值范围>
    testable_signal: <可测信号，描述如何验证该属性，供派生测试>
```

- 至少含 `applicability` / `constraints` / `testable_signal` 之一且机读；`testable_signal` 是派生测试源头。
- DomainEntity / Process 类在 SSOT §3 声明典型属性（文档化，非每实例强制全填）。

## 7. 组合规则

- `composed_of` 多个子实体时，高层实体有效属性 = 子实体 `attributes` 聚合（去重合并）。
- `configured_by` 表达实体由配置参数化（区别于物理部分）。
- 归纳（自底向上）：AI 从具体实例分析共性创建抽象 A，使实例 `specializes` A；`ontology-validate` 保证关系无环。

## 8. 与四层模型关系

- `layer` 字段（Evidence/Experience/Knowledge/Skill）保留资产来源层语义；本体重构跨四层物理归并（ADR-0030），但 `layer` 值不变。
- `records/*/evidence/`、`experience.md` 物理迁入 `ontology/`，新位置 frontmatter 保留 `source_task` 回链。

## 9. 门禁

- 新资产写入须经 `ontology-check` skill：合法 `type`、引用非空悬、`attributes` 有测试覆盖、知识实例有 `guides`/`relates_to`。
- **门禁的权威依据来自本体自身（meta-ontology）**：上述规则由 `ontology:concept/ontology-creation-gate` 承载，其 `relates_to` 指向六条规则节点 `ontology-rule-type-controlled`(AC-1)、`ontology-rule-non-dangling`(AC-2)、`ontology-rule-acyclic`(AC-3)、`ontology-rule-attr-testable`(AC-4)、`ontology-rule-richness`(AC-5)、`ontology-rule-guides-range`(AC-6)，并由 `ontology:concept/ontology-validate`（即 `scripts/ontology-validate.py`）执行。门禁不再是脚本自由定义，而是被 `meta-ontology` 节点显式授权。
- **节点是门禁参数的唯一事实源（B 方案落地，T0413）**：`scripts/ontology-validate.py` 在运行时读取 6 个 `ontology-rule-*` 节点的结构化 `rule_spec`（受控类型词表、关系键集合、属性测试字段名、知识资产类型、必需关系、范围约束等），据此真正执行 AC-1~AC-6 检查；原脚本硬编码常量被节点参数取代。规则节点缺失或 `rule_spec` 非法时校验器直接报错退出，不允许静默回退。改规则只改节点，校验行为自动跟随——文档/脚本漂移从源头消除。详见 `docs/adr/ADR-0035-meta-ontology-gate-runtime.md`。
- `ontology-validate.py` 校验（AC）：
  - **AC-1** `type` == 父目录名且 ∈ 受控词汇。
  - **AC-2** 关系/领域引用非空悬。
  - **AC-3** `specializes` 形成以 `Entity` 为根的无环图；所有关系图无环。
  - **AC-4** 每个 `attributes[].testable_signal` 非空。
  - **AC-5** 每 KnowledgeArtifact 实例至少 1 条 `guides` 或 `relates_to`（关系丰富度）。
  - **AC-6** `guides` 的 source 必为 KnowledgeArtifact 子类实例、target 必为 DomainEntity/Process 类节点。

## 10. 全流程闭环与硬门禁（T0414）

本体不仅是"创建时"的权威，更要贯穿 PDCA 全周期（plan→do→check→act→archive）并成为**提交级**硬门禁。三项补齐：

- **证据锚定（AC-1）**：`scripts/register-evidence.py` 在启动时从 `ontology/` 枚举 `pdca-evidence` 的全部子类型（`evidence-convergence-map`/`evidence-review`/`evidence-test-result`），建立 `kind 短名 → 本体节点 id` 允许表。`--kind` 必须在表内；命中子类型时写入 `evidence_type_ref = 本体节点 id` 并校验引用可解析；未知 kind 直接报错——证据自此机器锚定到本体。开发者可直接用短名（`convergence-map`/`review`/`test-result`，含别名 `test`→`test-result`）。
- **结论锚定（AC-2）**：`pdca-verdict` 现含完整三态子类型 `verdict-confirmed`/`verdict-rejected`/`verdict-partial`。`meta.verdict.outcome ∈ {confirmed,rejected,partial}` 必须映射到已存在的 `verdict-<outcome>` 节点；`scripts/ontology_gate.verdict_anchor_issues` 在 `check/act/archive` 阶段校验，映射缺失则阻断转换。
- **archive 本体自检（AC-3）**：`transition-phase.py` 目标为 `archive` 时自动调用 `scripts/ontology_gate.archive_ontology_ready_issues`——运行 `ontology-validate.py`（须通过）+ `ontology_graph.py --format summary`（须 `islands: 0`）；本体不合法/有孤岛则转换被拒，不得绕过。
- **提交级硬门禁（AC-4）**：共享门禁逻辑 `scripts/ci-ontology-gate.py` 跑 `ontology-validate` + 相关任务 `validate-convergence`，非零退出即阻断；`scripts/install-git-hook.sh`（可选安装，不静默改动 `.git/hooks`）装 `pre-commit` 钩子，`.github/workflows/ontology-gate.yml` 在远端 push/PR 时复跑同一检查。门禁从此不可被普通提交绕过。

设计取舍：plan/do/check/act 的本体"消费"保持顾问式（不阻断，避免 YAGNI 与吞吐损失）；仅**创建门禁、证据/结论锚定、archive 自检、CI/hook** 为硬门禁。详见 `docs/adr/ADR-0036-ontology-full-lifecycle-gate.md`。
