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

## 9. 流程如何消费本体（PDCA 全周期）

本体不是"plan 阶段声明一次就完事"，它在 PDCA 各阶段被主动消费（详见 `flows/flow-*/SKILL.md`）：

- **Plan（`flow-plan`）**：development/bugfix 任务须声明 `meta.ontology_fragment`（本任务构建/复用的本体目录或文件）；Do 前置 `ontology-ready` 关卡校验其存在且 `pdca.asset/v1` 结构合法。本体自举任务设 `meta.ontology_exempt=true` 豁免。
- **Do（`flow-do`）**：实现前/中对照 `meta.ontology_fragment`——复用既有 `id`/`type`/`relations`；新概念以 `pdca.asset/v1` frontmatter + `relations` 落盘到 `ontology/` 对应目录；变更后跑 `python3 scripts/ontology_graph.py --format summary` 确认无孤岛。`ontology_exempt` / 空片段则跳过。
- **Check（`flow-check`）**：development/bugfix 若 `ontology_fragment` 存在，须确认 `python3 scripts/ontology-validate.py` 通过且本体变更已在 `evidence/manifest.jsonl` 登记；Grill 追问"结论是否可被既有 ontology 节点 / `relations` 支撑"。
- **Act（`flow-act`）**：知识沉淀优先关联既有 ontology 节点而非孤立条目；架构改进若发现本体缺口（缺失节点 / 关系），创建本体补强任务（`meta.ontology_fragment` 指向待补强目录）。

> 本体消费的前提是 `meta.ontology_fragment` 存在；普通任务（片段为空或 `ontology_exempt`）不增加额外负担。

## 10. PDCA 流程现实时消费元本体知识（T0409）

T0409 在 T0408（对照任务领域本体片段）之上，进一步让流程**直接消费 PDCA 元本体本身的知识内容**作为执行指引，而不只是依赖静态 flow 文本：

- **补内容**：`pdca-*` 元本体节点（`phase-*`、`pdca-gate`、`pdca-ontology-ready`、`pdca-verdict`、`pdca-evidence`、`pdca-acceptance-criterion`、`pdca-task` 等）补全了正文知识——阶段定义/目的/进出条件/关键活动/对应 flow 文件、门禁理由、verdict 含义、证据含义。仅补 `# 标题` 之下正文，不动 frontmatter 的 `id/type/relations`，以免破坏 `ontology_reason` 推理。
- **pdca_context 脚本**：`scripts/pdca_context.py --phase <plan|do|check|act|archive>` 实时读取元本体，输出该阶段的（a）阶段定义（来自 `phase-<phase>.md` 正文）、（b）准入条件（`ontology_reason.admission_conditions`）、（c）合法后继（`ontology_reason.transition_targets`）、（d）关联概念知识（`pdca-gate-<phase>.relates_to` 指向节点的正文）。元本体缺失时回退硬编码提示，绝不中断流程。
- **接入点**：
  - `transition-phase.py` 转换成功后，将目标 phase 的 pdca_context 指引打印到 **stderr**（stdout 保持纯 JSON，不污染机器消费）。
  - `flow-plan/do/check/act` 入口均指令"运行 `python3 scripts/pdca_context.py --phase <x>` 读取本阶段定义/准入/合法后继作为执行指引"。
- **两层消费小结**：
  - 控制规则层（T0405）：`ontology_reason` 读元本体驱动转换/准入/证据识别。
  - 执行指引层（T0408+T0409）：Do/Check/Act 对照任务领域本体片段（T0408），并实时拉取 PDCA 元本体知识作为活指引（T0409）。

## 11. PDCA 元本体与经典方法论对齐说明（T0410）

T0410 用网络权威资料（ASQ / Deming Institute / Wikipedia / Lean Enterprise Institute / iSixSigma）核验了 `pdca-*` 元本体，并校正了两处与经典 PDCA 不符的地方：

- **校正 1：archive 不计入 PDCA 方法论阶段**。经典 PDCA 只有 **plan/do/check/act** 四阶段（ASQ 称 four-step model）。原 `pdca-phase.md` 把 `archive` 列为第五阶段，已改为：四阶段为方法论本体，`phase-archive` 仅作为**本工作流单任务生命周期的运维扩展终态**（正文见 `ontology:entity/phase-archive`）。
- **校正 2：补回"PDCA 是环"的语义**。经典 PDCA 是持续改进循环（act 之后回到 plan，ASQ："a circle has no end"）。原转换图 `plan→do→check→act→archive` 无任何回到 plan 的表达。新增 `ontology:concept/pdca-continuous-improvement` 承载 `act ↔ plan` 的循环关系，作为方法论层表达；单任务生命周期仍终止于 `archive`（保持 `ontology-validate` 无环、任务能终止）。
- **术语注记**：Deming 本人更偏好 **PDSA**（Plan-Do-**Study**-Act），Study 强调深度学习；PDCA 的 Check 是日方简化后的通俗变体。本工作流沿用 PDCA 命名（见 `pdca-phase.md`）。
- **设计原则**：任务转换图必须保持**无环**（否则单任务无法终止，且 `test_ac2_no_cycle_dangling` 会失败），故循环以**概念关系**表达，不新增 `transition-act-plan` 可执行边。
