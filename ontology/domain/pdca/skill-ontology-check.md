---
schema: pdca.asset/v1
id: ontology:domain/skill-ontology-check
name: ontology-check
summary: Check and validate ontology nodes against the schema.
description: 新本体资产写入前的门禁检查。校验 type 合法、引用非空悬、attributes 有 testable_signal，并与 ontology-validate.py 衔接。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-ontology-check/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/pdca-task
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


---
name: ontology-check
description: 新本体资产写入前的门禁检查。校验 type 合法、引用非空悬、attributes 有 testable_signal，并与 ontology-validate.py 衔接。
---

# Ontology Check

新资产（`ontology/<type>/<slug>.md`）写入前/后运行本门禁，确保符合 SSOT（`ontology/README.md`）。

> **门禁的权威依据来自本体（meta-ontology）**：本 skill 是 `ontology:concept/ontology-creation-gate` 的人工/流程入口；其 AC-1~AC-6 是 `ontology:concept/ontology-rule-*` 规则节点的镜像，最终由 `ontology:concept/ontology-validate`（`scripts/ontology-validate.py`）执行。门禁规则不是脚本自由定义，而是由 meta-ontology 显式授权——修改规则须先动对应 `ontology-rule-*` 节点。
>
> **节点是门禁参数的唯一事实源（B 方案，T0413）**：`ontology-validate.py` 运行时读取 6 个 `ontology-rule-*` 节点的 `rule_spec`（受控类型词表 / 关系键 / 属性测试字段 / 知识资产类型 / 必需关系 / 范围约束）并据此执行检查；硬编码常量已被节点参数取代。若校验器报错"规则节点缺失/rule_spec 非法"，说明本体未满足权威来源要求，须先修复 `ontology-rule-*` 节点，而非改脚本。

## 步骤

1. 确认 `<type>/` 目录名属于 SSOT v3 受控词汇（`domain`/`entity`/`concept`/`process`/`role`/`pattern`/`principle`/`pitfall`/`fact`/`decision`）或已在 README §4 登记扩展。知识形态实例按形态入 `pattern/`/`principle/`/`pitfall/`/`fact/`/`decision/`；领域实体实例入 `entity/`（或 `domain/`）。
2. frontmatter 满足 `pdca.asset/v1`：`schema=pdca.asset/v1`、`id`、`type`、`layer`、`summary`、`status`、`attributes[].{name,desc,constraint,testable_signal}`（KnowledgeArtifact 实例须有结构化 attributes，至少含 applicability/constraints/testable_signal 之一）。
3. `type` 必须等于父目录名（**目录即真理**）。
4. `relations.*` / `domain` 引用的 ontology id 必须在 `ontology/` 中存在对应节点（引用使用本体 id，如 `ontology:concept/foo`）。
5. 运行 `python3 scripts/ontology-validate.py --ontology-dir ontology`：必须 0 issues（否则拒绝写入/提交）。
6. 新增 KnowledgeArtifact 的 `attributes[].testable_signal` 不得为泛化描述（与 `ontology-validate` AC-4 衔接，脚本仅校验非空，人工门禁补位）：
    - 拒绝泛化：如 `由领域实践与测试验证`、`符合领域最佳实践` 等无法直接派生断言的描述
    - 合格要求：必须描述具体的验证动作、断言、工具或脚本（例："检查契约测试是否覆盖声明与实际的一致性断言"、"运行 seam_contract.py 对比 PRD 声明的 seam 清单与实际测试文件的一致性"、"执行 validate-convergence.py 检查 meta.convergence 回链完整性"）
    - 操作：人工复核新增/修改节点的每个 `testable_signal` 是否包含"动词+对象+判定标准"结构；抽样执行对应验证脚本并登记 evidence，拒绝纯泛化信号入库
    - 集成结算门禁：运行 `python3 scripts/check-research-ontology-settlement.py --task-dir <task>` 校验 `testable_signal` 精化程度，发现泛化信号即 `RESEARCH_SETTLEMENT_GENERIC_SIGNAL` 阻断写入

## 与 ontology-validate.py 的衔接

`ontology-validate.py` 是自动化执行者，覆盖：

- AC-1 `type==` 父目录名且 ∈ 受控词汇
- AC-2 关系/领域引用非空悬（relations 含 specializes/composed_of/configured_by/guides/relates_to 等）
- AC-3 `specializes` 形成以 `Entity` 为根的无环图；所有关系图无环
- AC-4 `attributes[].testable_signal` 非空（脚本仅机检非空，本 skill 步骤 6 人工补位校验非泛化；派生方法见 `ontology:pattern/testable-signal-to-test-derivation` 三模式：属性断言/契约测试/收敛验证）
- AC-5 每 KnowledgeArtifact 实例至少 1 条 `guides`/`relates_to`（关系丰富度）
- AC-6 `guides` 的 source 为 KnowledgeArtifact 子类实例、target 为 DomainEntity/Process 类
- 物理归并（见 `ontology:concept/ontology-creation-gate` 决策背景，原 ADR-0030）后 `ontology/domain/` 旧文件为 redirect 桩（frontmatter 含 `redirect_to` + `source_task`）；`ontology-validate.py` 现校验其目标存在（REDIRECT_DANGLING），桩指向的 `ontology/` 路径须真实存在。

本 skill 是其人工/流程入口；CI 或 `add` 知识流程应调用 `ontology-validate.py` 作为强制门禁（退出码非零即阻断）。

## 已知坑

- 引用必须使用本体 id（如 `ontology:concept/foo`），否则不被环检测/空悬检查覆盖。
- `README.md` 被脚本跳过，不是资产节点。
- 归纳（自底向上）创建抽象节点时，务必使实例 `specializes` 抽象，且抽象节点本身 `type` 与目录一致，否则 AC-1/AC-3 同时告警。
