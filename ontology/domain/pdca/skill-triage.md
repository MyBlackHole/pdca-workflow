---
schema: pdca.asset/v1
id: ontology:domain/skill-triage
name: triage
summary: Triage incoming tasks and prioritize based on impact and urgency.
description: |
  Classify issues as bug or enhancement, check for duplicates, verify the claim,
  grill if needed, and output an agent-ready task.json + prd.md + brief.

invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-triage/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/skill-invocation-contract
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# Triage — 任务分诊

分类 incoming tasks 并按 impact 和 urgency 优先级排序。

## 流程

1. 分类 issue 为 bug 或 enhancement（含 `research`：纯结论/报告，无可测试代码产出）
2. 检查重复
3. 验证 claim（事实性 claim 用代码/文档验证而非询问用户）
4. **Grill 门禁（强制分支）**：按 `grill-protocol` 先 Gather signal → Build ledger（resolved/open）→ Branch：
   - `research` 或输入仅含路径/单句（thin）→ **强制 `grill full`**（至少一轮 frontier，含推荐答案）
   - 其他 `mostly resolved` → 至少 **一次 `confirm-or-correct` 总结**（`Never zero-touch`：即使全 resolved 也必须一次显式确认，见 `ontology:concept/grilling-methodology`）
   - 仅当 ledger 显示全 resolved 且已获 `captured:true` 确认后，方可进入 5
5. 输出 agent-ready task.json + prd.md + brief（`final_confirmation` 必须绑定 `grilling` 轮次或 `confirm-or-correct` 摘要，纯自写无 ledger 视为门禁阻断）

## External PR 处理

Triage 扩展以处理外部 pull requests：

- PR 视为带附件的 issue，走相同角色、状态机和流程
- Discovery 仅暴露外部 PR
- bug-only 的"reproduce"步骤泛化为"verify the claim"
- 冗余检查解析已实现请求为 `wontfix`
- **HITL/AFK 分类**：外部 PR 需人工审核时为 HITL；可自动合并时为 AFK

## Model-Invoked 辅助

model-invoked 模式下，AI 可自动辅助 triage 流程：
- 自动分类 issue 类型
- 自动检查重复
- 自动生成 task.json + prd.md 草稿

## 已知坑

- 查重须搜活跃+归档 task 与 knowledge，事实性 claim 用代码/文档验证而非询问用户。
- PR 处理需 `triage` skill 已安装；外部 PR 默认关闭，需在 setup 中启用。
- HITL ticket 必须通过 live exchange 解决，不可由 agent 自主回答。
- **Grill 硬门禁**：`research/thin` 输入跳过 grill 或自写 `final_confirmation` 属 `timeline-integrity-gate` 违规；`Never zero-touch` 未满足时 `transition-phase` 应拒 `plan→do`。
- **Provenance 双态**：`clarifications.jsonl` 的 `captured:true` 仅用户原文，AI 代填一律 `false`（`skill-grilling:7`）；自问自答标 true 即 HITL 违规。