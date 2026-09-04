---
schema: pdca.asset/v1
id: ontology:process/flow-plan
type: process
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/flow-plan/1.0.0
summary: Plan 阶段流程实体：triage→Grill→PRD→任务拆解→final_confirmation 门禁
relations:
  specializes:
  - ontology:concept/process
  part_of:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/pdca-phase
  - ontology:entity/phase-plan
  - ontology:concept/pdca-architecture
  - ontology:concept/pdca-scenario-boundary-rule
  - ontology:concept/pdca-ai-friendly-confirmation
---

# PDCA Plan 流程（flow-plan）

Plan 阶段是 PDCA 周期的第一个阶段，产出经用户 `final_confirmation` 确认的 PRD 与任务拆解。

## 阶段步骤（权威描述）

1. **triage**：识别请求类别与 `scenario_type`，产出结构化 brief（AGENT-BRIEF 字段）。
2. **Grill（追问对齐）**：逐轮向用户追问，收敛需求与边界。**硬门禁**：`research` 或 thin 输入（仅路径/单句）强制至少一轮 `grilling`（frontier + 推荐答案），其他 `mostly resolved` 至少一次 `confirm-or-correct` 总结（`Never zero-touch`）；`final_confirmation` 必须绑定 `grilling` 的 `captured:true` 轮次或确认摘要，纯自写无 ledger 视为门禁阻断（见 `ontology:domain/skill-triage`）。
3. **方向确认**：与用户对齐方案，避免误解。
4. **PRD 撰写**：含 `### 验收标准` 复选框（门禁硬要求）。
5. **任务拆解（to-tickets）**：按 `meta.scenario_type` 拆分为子任务或票。
6. **final_confirmation 门禁**：用户明确确认立项后，方经 `transition-phase.py` 进入 Do（门禁校验 `captured:true` 来源，见 `scripts/pdca_core.py:gate_issues`）。

## 关键决策（已迁移自外部知识）

- **项目操作约定**：SKILL.md 的 frontmatter 与 body 分离管理（改 `meta.phase` 只动 frontmatter）；根文档（README/AGENTS/SKILLS-INDEX）手动 `git add+commit`；任务 ID 单调递增（扫 `pdca/tasks/` 与 `archive/` 取最大值+1）；flow 步骤须对应实际 skill 调用。
- **架构原则**（详 `ontology:concept/pdca-architecture`）：flow skill 是标准流程不可改，业务专有逻辑写 agent skill；资产分层 Evidence/Experience/Knowledge/Skill；阶段校验链 `phase → advance-phase → flow-<phase> 入口 → 步骤 → 手动推进`。
- **通用 kernel 原则**：PDCA 作为稳定外循环；领域行为由 `task.json.meta.scenario_type` 提供（6 条 Do 路径）；Check 产物是 Evidence；阶段 Decision 必须引用证据；Artifact 类型保持开放。
- **场景边界**（详 `ontology:concept/pdca-scenario-boundary-rule`）：含可测试代码产出（脚本/测试/可回归验证）→ `development`；纯结论性调研/报告 → `research`。
- **确认机制**（详 `ontology:concept/pdca-ai-friendly-confirmation`）：时间戳由 CLI 生成（`append-confirmation.py` 自动填真实 `at`）；失败须带 `guidance` 可执行；不可变记录只能由 CLI 变更（evidence 修正走 `--replace`）。

## 来源

- `（原知识层）architecture.md`
- `（原知识层）cli-behavior.md`
- `（原知识层）generic-ai-workflow-kernel.md`
- `（原知识层）scenario-boundary-rule.md`
- `（原知识层）ai-friendly-confirmation.md`
