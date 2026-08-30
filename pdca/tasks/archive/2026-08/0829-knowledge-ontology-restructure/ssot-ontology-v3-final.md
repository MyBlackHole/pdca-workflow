# SSOT 修订草案 v3（定稿候选，含自我审查修正）

> 自我审查依据：Gruber (1993) 五原则；Stanford Ontology 101；Palantir 四原则；Schema-vs-Ontology（atlan/puppygraph）；MDPI 属性/关系丰富度。
> 相对 v2 的修正：属性结构化、关系 domain/range、实例/类型区分、命名约定、关系词汇精简、Schema/Ontology 分层。

## 0. 自我审查发现的问题（v2 → v3）
1. **属性未结构化**（MDPI 警告：止步 taxonomy）：v2 映射的 attributes 仅文本摘要，无法派生测试。→ v3 规定 KnowledgeArtifact 实例必须有**结构化** attributes。
2. **关系无 domain/range 约束**：ontology 需定义每关系合法主体/客体，校验器加校验。
3. **实例 vs 类型风险**（Ontology 101）：md 文件是实例，specializes 指向类；须明文规定，避免后人把单篇当类。
4. **命名未统一**：类型 PascalCase，实例 id kebab-case。
5. **关系词汇过多**（Gruber 最小承诺）：6 种只用 4 种 → 保留核心 4 种，instance_of/part_of 标注可选/派生。
6. **composed_of 语义偏弱**：配置非物理部分 → 引入 `configured_by` 表达参数关系。

## 1. 实体类型层次（specializes = is-a / kind-of，≤3 层）
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
- **md 文件 = KnowledgeArtifact 实例**，通过 `specializes` 指向上述子类（实例 → 类）。
- 新增领域实体：加 `DomainEntity`/`Process` 子类；新增知识形态：加 `KnowledgeArtifact` 子类。满足 Gruber 可扩展。

## 2. 属性（结构化，核心防 taxonomy 退化）
- **Entity 子类**在 SSOT 中声明典型属性（文档化，非强制每实例全填）。
- **KnowledgeArtifact 实例**必须有结构化 attributes（frontmatter 或正文 `## 适用`/`## 约束`/`## 验收` 章节映射）：
  - `applicability`：适用场景/边界
  - `constraints`：约束/规则
  - `testable_signal`：可派生测试的信号/验收（呼应 Grill Q9"属性→测试"）
- 属性须**机读**（frontmatter 字段或固定章节标题），供 `ontology-validate.py` 抽取派生测试。

## 3. 关系（带 domain/range；核心 4 种 + 可选 2 种）
| 关系 | domain（主体） | range（客体） | 语义 |
|------|---------------|---------------|------|
| `specializes` | 任意实体/实例 | 父类（Entity 谱系） | is-a / kind-of，形成单根无环树 |
| `composed_of` | 整体实体 | 部分实体 | 真实部分-整体 |
| `configured_by` | 实体 | TLSConfiguration | 实体由某配置参数化 |
| `guides` | KnowledgeArtifact 实例 | DomainEntity/Process 类 | 知识指导某类实体 |
| `relates_to`（可选） | 任意 | 任意 | 跨文档关联（非 is-a 非组合） |
| `instance_of`/`part_of`（可选/派生） | — | — | 分别由 specializes/ composited_of 反向派生，不强制存储 |

## 4. Schema vs Ontology 分层
- `pdca.asset/v1` frontmatter = **schema**（语法契约：id/title/type/relations/source_ids 结构合法）。
- 本 SSOT = **ontology**（语义主干：类型/属性/关系/公理，可推理）。
- KG 实例 = 各 md 文件 + 其 relations 构成的图。

## 5. 目录 = 平铺索引
- 目录按 `type` 平铺（grill Q13），`type` 是索引标签。本体语义全在 `specializes`/`composed_of`/`configured_by`/`guides`/`relates_to` 图，不靠目录嵌套。

## 6. 校验器 AC（ontology-validate.py，更新）
- **AC1** type 受控 = {domain, entity, concept, process, role, pattern, principle, pitfall, fact, decision}，且 == 父目录名（目录即真相）。
- **AC2** `specializes` 形成以 `Entity` 为根的有向无环图。
- **AC3** 所有 relations 的 target id 非空悬（引用存在）。
- **AC4** `guides`/`configured_by`/`composed_of` 满足 domain/range 约束。
- **AC5** 每 KnowledgeArtifact 实例至少 1 条 `guides` 或 `relates_to`（关系丰富度，防 taxonomy 退化）。
- **AC6** 每 KnowledgeArtifact 实例含结构化 attributes（applicability/constraints/testable_signal 至少其一机读）。

## 7. 16 文件映射验证结论（见 tls-ontology-map-example.md）
- pattern=9 / principle=3 / pitfall=2 / fact=1 / decision=0，全为 KnowledgeArtifact 子类实例，经 `guides` 挂接领域实体类。
- 关系图（非树）成立；属性可派测试信号已识别。模型跨 16 真实文件可行。

## 8. 与四层模型 / ADR-0030（不变）
`layer` 字段与物理归并边界维持原约定；本修订只改 SSOT 语义层与校验器，不动归档产物结构（T0400/T0401 一致性处置见下条）。

## 9. T0400/T0401 归档产物一致性处置
- 已归档的 `ontology/README.md`（taxonomy 式）、`ontology-validate.py`、`ontology-check` 基于旧 type 词汇（pattern/principle/fact... 作 type）。
- 定稿后：在父任务 T0399 下写改进记录，说明 SSOT v3 实体本体模型取代 v1 taxonomy 模型；活跃文件同步更新，归档产物保留原状并标注"已被 v3 取代"于其 conclusion/evidence 索引。
- 不重写归档产物（保持不可变记录），仅在索引层注明演进。
