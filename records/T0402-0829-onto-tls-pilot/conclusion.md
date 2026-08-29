---
schema: pdca.asset/v1
id: T0402-0829-onto-tls-pilot
phase: check
source_ids: [ev-t0402-migration-manifest, ev-t0402-validate-pass, ev-t0402-acceptance-extra, ev-t0402-convergence-map-v3]
---

## 上下文
T0402 在 T0399（SSOT v3 实体本体模型）定稿后，将 `knowledge/` 下 16 个 tls 相关 md 物理迁移到 `ontology/`，按 v3 实体类型层次组织，并保持 record identity 不可变。这是 ADR-0030（物理归并）与 ADR-0031（md 承载+图库升级路径）的首次试点。

## 假设与结果
假设：v3 模型（实体类型层次 + 结构化 attributes + 关系图；知识形态作为 KnowledgeArtifact 子类经 `guides` 挂接领域/过程）可落地于 md 承载，并由 `ontology-validate.py` 形式化校验。结果：15 个类节点 + 16 个知识实例就位，校验器 AC1–AC6 全 PASS，record identity 保持。

## 分析
- **AC-1** ✅ 16 个文件全部迁入 `ontology/<type>/<slug>.md`，`type` 等于目录名且 ∈ v3 受控词汇（`ev-t0402-migration-manifest`）
- **AC-2** ✅ 类节点以 `Entity` 为根形成无环类型树（`specializes` 链：`pattern → knowledge-artifact → entity → concept/entity`），校验无环（`ev-t0402-migration-manifest`）
- **AC-3** ✅ 每个 KnowledgeArtifact 实例含结构化 `attributes`（applicability + testable_signal）；校验器 AC-4 验证 `testable_signal` 非空且全部通过（`ev-t0402-acceptance-extra` / `ev-t0402-validate-pass`）
- **AC-4** ✅ 每个知识实例至少 1 条 `guides`（或 `relates_to`）指向领域/过程类；fact 实例已补 `guides: [ontology:entity/exec-stdin-pump]`，校验器 AC-5 通过（`ev-t0402-acceptance-extra` / `ev-t0402-validate-pass`）
- **AC-5** ✅ `python3 scripts/ontology-validate.py --ontology-dir ontology` 输出 `OK: ontology 通过本体契约校验`（exit=0）（`ev-t0402-validate-pass`）
- **AC-6** ✅ 每个实例 frontmatter 含 `source_task` 回链；原 `knowledge/` 16 文件改写为 redirect 桩；`records/T0402-0829-onto-tls-pilot/` 壳与 `task.json meta.record` 保留（`ev-t0402-migration-manifest`）
- **AC-7** ✅ `records/*/evidence/` 下的 tls 代码/日志未迁移，仅 `knowledge/` 文本迁移且原位置保留 redirect，符合「保留不可变记录」的范围边界（`ev-t0402-acceptance-extra`）

## 失败原因
无（全部 AC 满足）。

## 适用边界
- 仅覆盖 tls 域试点；`records/*/evidence/` 代码/日志的归并留待 T0403 全量迁移处理。
- 当前以 md 承载本体（ADR-0031）；frontmatter 图中立模型确保未来可零丢失迁移至图数据库（Neo4j property graph / RDF triple store）。
- `attributes.testable_signal` 目前为语义描述，尚未派生自动化测试；更细的 testable 细化见「下一轮建议」。

## 下一轮建议
- T0403 全量迁移可复用本任务的迁移脚本与 frontmatter 模板。
- 对 `attributes.testable_signal` 做更细结构化（如可机读断言），以便从知识资产派生回归测试，落实 v3「属性可派生测试」的设计意图。
- 在 `skills/ontology-check` 增加「实例 → 派生测试」接线示例，巩固 Do→Check 的可验证闭环。

## Verdict
- outcome: confirmed
- reason: 7 条 PRD 验收标准全部满足，ontology-validate.py 形式化校验全 PASS，record identity 经 source_task + redirect 桩保持，convergence-map 与证据齐备。
- verdict_id: T0402-verdict-1
- at: 2026-08-29T19:23:30+08:00
