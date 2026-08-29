# T0400 检查结论

## 收敛条件
Plan 收敛语句：`ontology SSOT vocabulary and pdca.asset/v1 frontmatter schema are defined and mapped to evidence`

## 自我审查（Check 阶段补充）
审查发现并修正以下缺陷，确保 SSOT 可作为后续任务统一规范：
- **硬矛盾已修正**：原 §2 称"type 不在 frontmatter 冗余存储"，与 schema `required` 含 `type` 冲突。现统一为——frontmatter 保留 `type` 且**必须 == 父目录名**，`ontology-validate` 校验一致（目录为权威源，字段为镜像）。
- **类型选择指南已补**：§3 新增归纳时 concept/pattern/principle/pitfall/decision/process 的选择标准，避免 AI 归纳时类型混乱。
- **domain 语义已澄清**：§2 区分 `domain/<entity>.md`（领域实体节点）与 frontmatter `domain` 字段（所属领域标签数组）。

## 验收判定
- **AC-1** ✅ — `ontology/README.md` 定义类型受控词汇、关系词汇表、attributes 结构、组合规则、目录即真理约定，并已修正 type 矛盾（证据 `ssot-readme-v3`）
- **AC-2** ✅ — `schemas/ontology-asset.schema.json` 定义 pdca.asset/v1 扩展 frontmatter 结构（id/type/layer/attributes/relations/domain/source_ids/also_type/confidence/status），`type` 为 required 且由 `ontology-validate` 校验等于目录名（证据 `asset-schema`）
- **AC-3** ✅ — README §1 明确三合一用途、§7 引用 ADR-0030 的"全部物理归并"边界（证据 `ssot-readme-v3`）

## 证据映射
convergence map（证据 `convergence-v4`）：单收敛项回链 AC-1/AC-2/AC-3，全部指向非 map 证据（`ssot-readme-v3`、`asset-schema`），无空悬引用。

## Verdict
- outcome: confirmed
- reason: AC-1/AC-2/AC-3 全部满足；自我审查发现的 type 矛盾已修正，证据 ssot-readme-v3 / asset-schema / convergence-v4 齐全无空悬，可作后续统一规范基础
- verdict_id: V-T0400-0001
- at: 2026-08-29T18:17:00+08:00
