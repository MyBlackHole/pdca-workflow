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
| PDCA 作为稳定外循环 | `ontology/process/flow-{plan,do,check,act}.md` |
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

## 决策背景（项目架构设计：六维缺陷与解决方案，原 docs/project-architecture-design.md）

PDCA 是一套统一协议，用同一套机制同时消除 AI 代理执行的六个维度系统性缺陷；任一维度缺失都会使协议不完整，每个门禁/阶段/产物都对应至少一个具体缺陷。

- **方向控制失灵**：需求理解偏差/过度承诺/目标丢失/隐含假设 → grill 多轮追问至 final_confirmation、triage 分诊、Check 逐项核验、clarifications.jsonl 留痕。
- **执行路径混沌**：无标准流程/无顺序/无终止/重复造轮 → flows/ 四阶段固定顺序 + flow-do 按 `meta.scenario_type` 路由 6 条路径（development/bugfix/research/documentation/design/review）+ 收敛检验。
- **质量不可信**：无产出标准/无检验/无证据链/无质量把关 → prd.md 验收条件 + check 对照 PRD 与证据 + register-evidence 证据链 + code-review 双轴审查。
- **记忆归零**：跨会话失忆/经验不传承/知识不生长/无从检索 → records/ 不可变记录 + ontology/domain/ 可复用知识 + flow-act 知识处置（Evidence→Experience→Knowledge→Skill）+ （来源回链由节点 frontmatter 承载，废弃 manifest.jsonl） 索引 + CONTEXT.md 术语统一。
- **黑箱执行**：不可审计/不可解释/不可回滚/无进展感知 → task.json 阶段流转 + records/ 追踪 + rollback-phase.sh / advance-phase 快照 + journal 日志。
- **多项目混乱**：项目混杂/知识隔离/权限混淆/环境依赖 → external_project 字段 + init-external.sh 解耦 + 共享 $PDCA_HOME 知识库 + permission.external_directory 配置。

**五层架构**：用户交互层（ask-matt→triage→grill）→ 执行引擎层（Plan→Do→Check→Act→archive，场景路由，final_confirmation 与收敛检验门禁）→ 技能指令层（model-invoked 与 user-invoked 技能）→ 数据存储层（pdca/tasks、records 不可变、knowledge、journal、ontology）→ 合约层（AGENTS.md 唯一入口、CONTEXT.md 术语表、templates、scripts）。

**架构决策原则**：flow skill 不可修改（业务逻写在 agent skill）；资产分层逐级提炼；门禁保护（Plan→Do 的 final_confirmation 与 archive 自检）；records/ 不可变；跨任务决策写入本体节点「决策背景」段（原 ADR 机制已退役）；YAGNI。
