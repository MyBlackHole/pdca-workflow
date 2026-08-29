---
name: ontology-check
description: 新本体资产写入前的门禁检查。校验 type 合法、引用非空悬、attributes 有 testable_signal，并与 ontology-validate.py 衔接。
---

# Ontology Check

新资产（`ontology/<type>/<slug>.md`）写入前/后运行本门禁，确保符合 SSOT（`ontology/README.md`）。

## 步骤

1. 确认 `<type>/` 目录名属于 SSOT 受控词汇（`concept`/`principle`/`pattern`/`pitfall`/`decision`/`fact`/`process`）或已在 README §3 登记扩展。
2. frontmatter 满足 `pdca.asset/v1`：`schema=pdca.asset/v1`、`id`、`type`、`layer`、`summary`、`status`、`attributes[].{name,desc,constraint,testable_signal}`。
3. `type` 必须等于父目录名（**目录即真理**）。
4. `relations.*` / `domain` 引用的 ontology id 必须在 `ontology/` 中存在对应节点（引用使用本体 id，如 `ontology:concept/foo`）。
5. 运行 `python3 scripts/ontology-validate.py --ontology-dir ontology`：必须 0 issues（否则拒绝写入/提交）。

## 与 ontology-validate.py 的衔接

`ontology-validate.py` 是自动化执行者，覆盖：

- AC-1 `type==` 父目录名
- AC-2 关系/领域引用非空悬
- AC-3 关系图无环（DAG）
- AC-4 `attributes[].testable_signal` 非空

本 skill 是其人工/流程入口；CI 或 `add` 知识流程应调用 `ontology-validate.py` 作为强制门禁（退出码非零即阻断）。

## 已知坑

- 引用必须使用本体 id（如 `ontology:concept/foo`），否则不被环检测/空悬检查覆盖。
- `README.md` 被脚本跳过，不是资产节点。
- 归纳（自底向上）创建抽象节点时，务必使实例 `specializes` 抽象，且抽象节点本身 `type` 与目录一致，否则 AC-1/AC-3 同时告警。
