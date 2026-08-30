# SSOT 修订草案 v2（基于本体工程方法论）【已取代】

> **状态：SUPERSEDED** — 本草案已被 `ssot-ontology-v3-final.md` 取代；v3 已落地为活跃 `ontology/README.md`。本文件仅保留为设计演进历史。
> 依据：Gruber (1993) 本体设计原则；Stanford Ontology 101；Palantir Ontology Best Practices；Schema-vs-Ontology 区分（atlan/puppygraph）；MDPI 属性丰富度研究。
> 核心修正：之前草案把知识形态降维成属性，仍残留 taxonomy 思维。本体应是**图**：实体类型层次（is-a）+ 属性（描述实体）+ 关系（连接实体），支持推理。

## 1. 本体核心 = 实体类型 + 属性 + 关系图
- **实体类型层次**：用 `specializes`（is-a / kind-of）组织。`A specializes B` ⟺ A 是 B 的一种。
  - 例：`Entity` → `DomainEntity` → `TLS` → `TLSSession` / `MTLSHandshake` / `X509Certificate`。
  - 避免 "single X subclasses all X"；命名单数/复数统一（Ontology 101）。
- **属性（attributes）**：每个类型用 attributes 描述"它到底是什么样子"（特征/约束/可测信号）。**属性是本体核心，类层次只是骨架**（MDPI 警告缺失属性即退化为 taxonomy）。
- **关系（relations）**：除 is-a 外必须有 `composed_of` / `guides` / `relates_to` / `part_of` / `instance_of`，形成**图**而非树。关系丰富度是质量指标。

## 2. 知识形态 = 独立知识实体类型（非维度）
- `Pattern` / `Principle` / `Pitfall` / `Fact` / `Decision` 是 **`KnowledgeArtifact` 的子类**（specializes 它），自身有 attributes（适用条件/步骤/反例），通过 `guides` 关系挂接到领域实体类型。
- 例：`pattern/mtls-handshake-enum-unify` specializes `KnowledgeArtifact`，`knowledge_form=pattern`，`guides` `entity/mtls-handshake`。

## 3. 组合优于深继承（Composition over deep hierarchies）
- 复杂实体用 `composed_of` 表达"由子实体组合"，而非无限 is-a 细分（Palantir #4）。
- 共享特征用 `also_type` / 角色接口，不建脆弱的深层父类（避免 God Object）。

## 4. 建模真实实体，而非系统/文件（Model reality not systems）
- 节点表示领域真实实体（tls-session、certificate、handshake），不表示文件、目录或知识形态分类。这是"本体论组织"的本质（Palantir #1）。

## 5. schema 与 ontology 分层
- `pdca.asset/v1` frontmatter = **schema**（语法契约：字段结构合法）。
- SSOT 定义 = **ontology**（语义层：类型/属性/关系/公理，可推理）。
- 校验器同时校验：schema 合法性 + ontology 语义（type==目录、引用非空悬、关系无环、属性→测试）。

## 6. 目录 = 平铺索引（非本体结构）
- 目录按 `type` 平铺（符合 grill Q13），`type` 是索引标签。本体语义全在 `specializes` / `composed_of` / `guides` 关系图，不靠目录嵌套。

## 7. 示例（tls 本体图）
```
Entity
 ├─ DomainEntity ── specializes ──> Entity
 │    └─ TLS ── specializes ──> DomainEntity
 │         ├─ TLSSession  (attributes: 角色/阶段/算法协商/凭据路径)
 │         │    composed_of: [MTLSHandshake, X509Certificate]
 │         │    guided_by:   [principle/structured-mtls-failure-diagnostics]
 │         ├─ MTLSHandshake (attributes: 枚举名称映射/网络序/兼容别名)
 │         │    guided_by:   [pattern/mtls-handshake-enum-unify, pitfall/mtls-handshake-netorder]
 │         └─ X509Certificate (attributes: 重载安全/校验路径)
 └─ KnowledgeArtifact ── specializes ──> Entity
      ├─ Pattern   (knowledge_form) ── guides ──> MTLSHandshake
      ├─ Principle (knowledge_form) ── guides ──> TLSSession
      └─ Pitfall   (knowledge_form)
```

## 8. 校验器 / 门禁影响
- `ontology-validate.py`：type 受控词汇改为实体类别（domain/entity/concept/process/role + knowledge 子类）；AC 增加：relation-richness 提示、`knowledge_form` 受控、`guides`/`guided_by` 引用非空悬、属性覆盖测试。
- `ontology-check` skill 同步更新。

## 9. 与四层模型 / ADR-0030（不变）
`layer` 字段与物理归并边界维持原约定。
