# ONTOLOGY_GUIDE

> 设计原则：**先人后机**。用人类最易读的 Markdown 构建知识骨架，把"语义真理"放在机器可校验的 frontmatter 里，一个脚本即可无损转为 OWL/RDF。本指南**兼容吸收** `pdca.asset/v1` 体系（SSOT v3），不替换它。

> 存放位置：本文档位于 `docs/ONTOLOGY_GUIDE.md`，**不属于** `ontology/` 节点（避免破坏 `ontology-validate`）；`ontology/_meta.yaml` 仍为 `.yaml` 不被扫描，留于 `ontology/` 根。

## 0. 与 README.md 的关系
- `ontology/README.md` 是**契约权威**：定义类型词汇、关系 range、`ontology-validate` 规则。
- 本指南是**使用约定**：教人如何写/读节点，并说明"语义权威 = frontmatter + relations"。
- 二者冲突时以 README 为准。

## 1. 语义权威（唯一事实源）
每个 `.md` 文件的 `pdca.asset/v1` frontmatter + YAML `relations:` 块，是本体身份与关系的**唯一事实源**，由 `ontology-validate` 强制校验。目录位置只作人类阅读索引，不决定语义（`type` 字段必须等于父目录名，这是 SSOT v3 的强约束，便于定位与校验）。

## 2. 强制 Frontmatter（"身份证"）
```yaml
---
schema: pdca.asset/v1
id: ontology:entity/x509-certificate      # 全局唯一 ID，无视存放目录
type: entity                               # 受控词汇：domain/entity/concept/process/role/pattern/principle/pitfall/fact/decision
layer: Knowledge
status: active
summary: 一句话定义
# —— 可选人读增强（不影响机器语义，且均非受控引用）——
docType: Entity                           # 自由文本人类阅读索引标签
tags: [x509, cert]                        # 自由文本标签，便于过滤
# domain: [ontology:domain/tls-mtls]      # 若使用须为「列表」且指向已存在的 domain/* 节点（受控引用），非自由文本
relations:
  specializes: [ontology:concept/domain-entity]
  guides: [ontology:entity/tls-session]
attributes:
  - name: serialNumber
    desc: 证书序列号
    constraint: ""
    testable_signal: 序列号唯一且可比对
---
```

## 3. 关系表达：YAML `relations:` 块（机器可校验）
```yaml
relations:
  specializes: [ontology:concept/domain-entity]   # → rdfs:subClassOf
  guides:     [ontology:entity/tls-session]       # → owl:ObjectProperty(pdca:guides)
  composed_of: [...]                               # 顺序敏感（转换方向）
  configured_by: [...]
  relates_to: [...]
```
- 受控谓词 + range 校验（如 `guides` 仅指向 KnowledgeArtifact 类）→ **无损映射 OWL**，拼写错误会被 `ontology-validate` 抓住。
- 正文里**也可以**写 `[[wikilink]]` 帮助人读，但必须视为 `relations` 的镜像；新增关系请先写 `relations`，再（可选）在正文补链接。

## 4. 属性：YAML `attributes:` 块（带语义，不只有类型）
```yaml
attributes:
  - name: serialNumber
    desc: 证书序列号                         # 承载语义描述
    constraint: ""
    testable_signal: 序列号唯一且可比对       # 可测信号，利于自动校验
```
相比"二级列表只写数据类型"，SSOT 的 attributes 同时保留**描述与可测信号**，转 OWL 时数据属性不丢语义。

## 5. 概念文件夹（`concept/`）作类型字典
把 `concept/domain-entity.md` 视作顶层抽象，在其中注明其子类索引：
```markdown
# 领域实体 (Domain Entity)
**定义**: 核心业务对象抽象。
**本目录下的子类包括**: `ontology:entity/x509-certificate`, `ontology:entity/tls-session`
```
目录仅作人类阅读索引；真正的层级由 `relations.specializes` 决定。

## 6. 根目录 `_meta.yaml`
```yaml
# 本仓库顶级文件夹（concept/ entity/ pattern/ ...）仅作人类阅读索引。
# 语义权威 = 各 .md 文件的 pdca.asset/v1 frontmatter + YAML relations 块。
# 正文 [[wikilink]] 为派生视图，非关系来源；任何关系变更须先改 relations。
```

## 7. 升华路径（已验证）
`scripts/ontology_graph.py` 与 `scripts/proto_ontology_to_owl.py`（调研原型）证明：读取 `id/type/relations/attributes` →
- `owl:Class` / `rdfs:subClassOf` / `owl:ObjectProperty` / `owl:DatatypeProperty` 是**直接且无损**的；
- `ontology_graph.py` 还可导出 Obsidian 兼容图谱并检测**孤岛节点**（无 relations 连线的节点），用于可视化自检。

未来正式升华脚本只需三件事：
1. 遍历 `ontology/**.md`；
2. `relations.specializes` → `rdfs:subClassOf`，其余关系 → `owl:ObjectProperty`；
3. `attributes` → `owl:DatatypeProperty`（含 desc/testable_signal 注解）。

## 8. 可视化（Obsidian / Foam）
直接用 Obsidian 打开 `ontology/` 目录即可获得关系图谱视图；`scripts/ontology_graph.py` 进一步输出结构化图谱与孤岛清单，弥补纯 wikilink 无法被机器校验的短板。

> 结论：用户的"先人后机 / 可视化 / 脚本升华"精神**全部保留**，只是把"语义事实"从易错的正文 wikilink 收到机器可校验的 frontmatter，从而在不返工现有资产的前提下达成目标。
