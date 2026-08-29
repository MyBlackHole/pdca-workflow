<!-- DRAFT — 调研草案（T0406），尚未采纳，不改变现有 SSOT v3 约定 -->
<!-- 若未来采纳，应移至 ontology/ONTOLOGY_GUIDE.md 并入 README，并另立任务/ADR -->

# ONTOLOGY_GUIDE（草案·兼容吸收版）

> 设计原则：**先人后机**。用人类最易读的 Markdown 构建知识骨架，把"语义真理"放在机器可校验的 frontmatter 里，未来一个脚本即可无损转为 OWL/RDF。本草案在**不推翻 SSOT v3** 的前提下，吸收"Markdown 草拟工作法"的可取内核。

## 0. 一句话定位
- **机器权威**：每个 `.md` 文件的 `pdca.asset/v1` frontmatter + YAML `relations:` 块，是本体身份与关系的唯一事实源（由 `ontology-validate` 强制校验）。
- **人类视图**：正文 `[[wikilink]]`、目录归档、Obsidian 图谱，都是 frontmatter 的**可读镜像**，不是关系来源。
- **升华脚本**：`scripts/ontology_graph.py`（规划中，见 ADR-0031）从 frontmatter+relations 一键导出 OWL/TTL 与 Obsidian 图谱。

## 1. 强制 Frontmatter（"身份证"，唯一身份依据）
```yaml
---
schema: pdca.asset/v1
id: ontology:entity/x509-certificate      # 全局唯一 ID，无视存放目录
type: entity                               # 受控词汇：domain/entity/concept/process/role/pattern/principle/pitfall/fact/decision
layer: Knowledge
status: active
summary: 一句话定义
# —— 可选人读增强（不影响机器语义）——
domain: TLS/mTLS                          # 顶级领域标签，便于过滤
docType: Entity                           # 人类阅读索引标签
tags: [x509, cert]
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
要点：身份由 `id`/`type` 决定，**不**由文件夹名推断（但 `type` 必须等于父目录名，这是 SSOT v3 的强约束，便于快速定位与校验）。

## 2. 关系表达：YAML `relations:` 块（机器可校验）
```yaml
relations:
  specializes: [ontology:concept/domain-entity]   # → rdfs:subClassOf
  guides:     [ontology:entity/tls-session]       # → owl:ObjectProperty(pdca:guides)
  composed_of: [...]                               # 顺序敏感（转换方向）
  configured_by: [...]
  relates_to: [...]
```
- 受控谓词 + range 校验（如 `guides` 仅指向 KnowledgeArtifact 类）→ **无损映射 OWL**，且拼写错误会被 `ontology-validate` 抓住。
- 正文里**也可以**写 `[[wikilink]]` 帮助人读，但必须视为 `relations` 的镜像；新增关系请先写 `relations`，再（可选）在正文补链接。

## 3. 属性：YAML `attributes:` 块（带语义，不只有类型）
```yaml
attributes:
  - name: serialNumber
    desc: 证书序列号                         # 承载语义描述
    constraint: ""
    testable_signal: 序列号唯一且可比对       # 可测信号，利于自动校验
```
相比"二级列表只写数据类型"，SSOT 的 attributes 同时保留**描述与可测信号**，转 OWL 时数据属性不丢语义。

## 4. 概念文件夹（`concept/`）作类型字典
把 `concept/domain-entity.md` 视作顶层抽象，在其中注明其子类索引：
```markdown
# 领域实体 (Domain Entity)
**定义**: 核心业务对象抽象。
**本目录下的子类包括**: `ontology:entity/x509-certificate`, `ontology:entity/tls-session`
```
目录仅作人类阅读索引；真正的层级由 `relations.specializes` 决定。

## 5. 根目录 `_meta.yaml`
```yaml
# 本仓库顶级文件夹（concept/ entity/ pattern/ ...）仅作人类阅读索引。
# 语义权威 = 各 .md 文件的 pdca.asset/v1 frontmatter + YAML relations 块。
# 正文 [[wikilink]] 为派生视图，非关系来源；任何关系变更须先改 relations。
```

## 6. 升华路径（已原型验证）
`proto_ontology_to_owl.py` 已证明：读取 `id/type/relations/attributes` → 生成 `owl:Class` / `rdfs:subClassOf` / `owl:ObjectProperty` / `owl:DatatypeProperty` 是**直接且无损**的。未来正式脚本只需三件事：
1. 遍历 `ontology/**.md`；
2. `relations.specializes` → `rdfs:subClassOf`，其余关系 → `owl:ObjectProperty`；
3. `attributes` → `owl:DatatypeProperty`（含 desc/testable_signal 注解）。

## 7. 与原"Markdown 草拟工作法"提案的差异（为何不照搬）
| 提案点 | 本草案处理 | 原因 |
|--------|-----------|------|
| `type: Class/Individual` + `superClass` | 用受控 `type` + `relations.specializes` | 受控词汇可被 `ontology-validate` 校验，免归一化层 |
| 正文 `[[wikilink]]` 作为关系来源 | 降级为派生视图 | 自由文本谓词需归一化、拼错静默断图、易与 frontmatter 双重表达分裂 |
| 属性仅"数据类型 X" | 用 `attributes[]` 带 desc/testable_signal | 保值语义，转 OWL 不丢信息 |
| `_meta.yaml` 称"文件夹不参与层级" | 称"文件夹为索引，权威=frontmatter+relations" | 与 SSOT v3 `type==目录名` 共存，避免语义分裂 |

> 结论：用户的"先人后机 / 可视化 / 脚本升华"精神**全部保留**，只是把"语义事实"从易错的正文 wikilink 收到机器可校验的 frontmatter，从而在不返工现有资产的前提下达成目标。
