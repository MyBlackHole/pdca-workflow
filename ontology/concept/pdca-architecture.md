---
schema: pdca.asset/v1
id: ontology:concept/pdca-architecture
type: concept
layer: Knowledge
status: active
summary: PDCA 工作流核心资产边界与架构原则（flow/agent skill 分工、资产分层、阶段校验链、通用 kernel）
relations:
  specializes:
  - ontology:concept/pdca
  relates_to:
  - ontology:concept/process
  - ontology:concept/pdca-task
---

# PDCA 架构（pdca-architecture）

## 原则

- **flow skill 与 agent skill 分工**：flow skill 永远是标准流程，不可修改或自定义；业务专有逻辑写在 agent skill 中。反例：曾尝试自定义 `flow-web-research`，后更正为标准 flow skills + `web-research` agent skill。
- **资产分层**：可检索资产分 Evidence / Experience / Knowledge / Skill 四层。Evidence 只索引摘要，Experience 按需追溯，Knowledge/Skill 是默认上下文候选。新增资产同步 `manifest.jsonl`。
- **阶段校验顺序**：`phase 字段 → advance-phase 门禁 → 对应 flow-<phase> 入口条件 → 步骤执行 → 手动 phase 推进`。

## 通用 AI 工作流 Kernel 原则（已落地）

| 原则 | 当前体现 |
|------|---------|
| PDCA 作为稳定外循环 | `flows/flow-{plan,do,check,act}/SKILL.md` |
| 领域行为由场景契约提供 | `task.json` → `meta.scenario_type` → 6 条 Do 路径 |
| Check 产物是 Evidence | `records/<id>/evidence/` + `manifest.jsonl` |
| 阶段 Decision 必须引用证据 | flow-check 的 verify-convergence 门禁 |
| Artifact 类型保持开放 | 文件、URL、报告均可作为证据 |

## 项目操作约定（cli-behavior）

- SKILL.md frontmatter 与 body 分离管理：改 `meta.phase`/`scenario_type` 只动 frontmatter。
- 根文档（README/AGENTS/SKILLS-INDEX）手动 `git add + commit`；`scripts/` 工具各自文件白名单。
- 任务 ID 必须单调递增：扫 `pdca/tasks/` 与 `archive/` 取最大值+1。
- 新建 skill ID 不与已有重名；flow 步骤须对应实际 skill 调用。

## 来源

- `（原知识层）architecture.md`
- `（原知识层）generic-ai-workflow-kernel.md`
- `（原知识层）cli-behavior.md`

## 决策背景（原 ADR-0032：本体驱动 PDCA）
- 背景：PDCA 流程的门禁/转换逻辑曾散落在 transition-phase.py 与 flow-*.md 的硬编码枚举与文本约定，规则不可机读、不可演进。
- 决策：将本体提升为 PDCA 流程一等公民；门禁/转换逻辑全本体化（两层本体：PDCA 元本体 + 领域本体）；ontology-ready 关卡驱动 do 准入；meta 增 ontology_fragment / ontology_exempt。
- 影响：transition-phase 改由元本体驱动；ontology_fragment 成为开发类任务强约束入口；复用既有 ontology-validate。
