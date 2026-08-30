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

## 与 ontology-validate.py 的衔接

`ontology-validate.py` 是自动化执行者，覆盖：

- AC-1 `type==` 父目录名且 ∈ 受控词汇
- AC-2 关系/领域引用非空悬（relations 含 specializes/composed_of/configured_by/guides/relates_to 等）
- AC-3 `specializes` 形成以 `Entity` 为根的无环图；所有关系图无环
- AC-4 `attributes[].testable_signal` 非空
- AC-5 每 KnowledgeArtifact 实例至少 1 条 `guides`/`relates_to`（关系丰富度）
- AC-6 `guides` 的 source 为 KnowledgeArtifact 子类实例、target 为 DomainEntity/Process 类
- 物理归并（见 `ontology:concept/ontology-creation-gate` 决策背景，原 ADR-0030）后 `ontology/domain/` 旧文件为 redirect 桩（frontmatter 含 `redirect_to` + `source_task`）；`ontology-validate.py` 现校验其目标存在（REDIRECT_DANGLING），桩指向的 `ontology/` 路径须真实存在。

本 skill 是其人工/流程入口；CI 或 `add` 知识流程应调用 `ontology-validate.py` 作为强制门禁（退出码非零即阻断）。

## 已知坑

- 引用必须使用本体 id（如 `ontology:concept/foo`），否则不被环检测/空悬检查覆盖。
- `README.md` 被脚本跳过，不是资产节点。
- 归纳（自底向上）创建抽象节点时，务必使实例 `specializes` 抽象，且抽象节点本身 `type` 与目录一致，否则 AC-1/AC-3 同时告警。
