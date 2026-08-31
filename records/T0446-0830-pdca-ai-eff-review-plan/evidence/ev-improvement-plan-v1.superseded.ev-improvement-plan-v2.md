# 带优先级的改进计划：本地 PDCA 本体 vs mattpocock/skills v1.2.3

## P0 — 安全/门禁类（立即推进）

### P0-1: Phase Boundary 五选项决策树
- **改进项**：在 flow-do 收尾阶段嵌入 Phase Boundary 五选项决策树（Continue/Clear/Handoff/Subagent/Compact）
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Phase Boundary 子节点）
- **关联任务**：待创建（建议 T0447）
- **验证方式**：flow-do 收尾时，session 处于 mid-phase 应触发五选项树；五分支均有用例覆盖
- **收敛条件**：flow-do 收尾脚本包含五选项树逻辑，且至少 1 个测试用例通过每分支

### P0-2: Grounding 依赖图写作法
- **改进项**：在 writing-for-agents 体系中增加 grounding 声明规则（每 beat 声明 requires/grounds，候选续写只能从当前 grounded 集合可达）
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Grounding 子节点）
- **关联任务**：待创建（建议 T0447）
- **验证方式**：writing-for-agents 技能包含 grounding 声明模板；长文档生成时可检查每节声明
- **收敛条件**：writing-for-agents 技能新增 grounding 节，且存在可运行的示例

## P1 — 能力补齐类（次优先推进）

### P1-1: Wait-what 重述机制
- **改进项**：新建 wait-wait 技能或在 writing-for-agents 中增加 re-pitch 规范（符合 ASD-STE100 Simplified Technical English）
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Wait-what 子节点）
- **关联任务**：待创建（建议 T0448）
- **验证方式**：存在专用 wait-wait 技能文件；re-pitch 流程符合 ASD-STE100 规范
- **收敛条件**：wait-wait 技能文件存在且通过 ontology-check；re-pitch 示例可运行

### P1-2: SKILL-MECHANICS 前言规范
- **改进项**：所有 SKILL.md 补充 `policy.allow_implicit_invocation` 字段，增加 user-invoked/model-invoked 显式调用选择逻辑
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（SKILL-MECHANICS 子节点）
- **关联任务**：待创建（建议 T0448）
- **验证方式**：所有 SKILL.md 包含 `policy.allow_implicit_invocation` 字段；存在调用选择逻辑文档
- **收敛条件**：全部现有 SKILL.md 补充字段，新增技能模板包含该字段

## P2 — 细节完善类（最后推进）

### P2-1: Docs Page 四节模式
- **改进项**：新增 writing-docs.md 模板，定义 docs page 四节模式（What it does / When to reach for it / Common questions / It's working if）
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Docs Page 子节点）
- **关联任务**：待创建（建议 T0449）
- **验证方式**：writing-docs.md 模板存在；新技能文档遵循四节模式
- **收敛条件**：writing-docs.md 模板可引用，新技能文档模板包含四节

### P2-2: Repo 配置技能
- **改进项**：新建 repo 配置技能（issue tracker/triage labels/domain docs 初始化），适配 pdca 非 Claude 插件架构
- **关联本体节点**：`ontology/domain/ai-efficiency.md`（Setup 子节点）
- **关联任务**：待创建（建议 T0449）
- **验证方式**：repo 配置技能存在；新项目可通过该技能完成初始化
- **收敛条件**：配置技能文件存在，初始化流程可运行

## 计划概要

| 优先级 | 改进项 | 关联任务 | 验证方式 | 收敛条件 |
|--------|--------|----------|----------|----------|
| P0 | Phase Boundary 五选项树 | T0447 | 五分支用例覆盖 | flow-do 收尾包含决策树 |
| P0 | Grounding 依赖图 | T0447 | 每节声明检查 | writing-for-agents 新增 grounding 节 |
| P1 | Wait-what 重述机制 | T0448 | ASD-STE100 规范 | wait-wait 技能通过 ontology-check |
| P1 | SKILL-MECHANICS 前言 | T0448 | 字段存在性检查 | 全部 SKILL.md 补充字段 |
| P2 | Docs Page 四节模式 | T0449 | 模板可引用 | writing-docs.md 模板存在 |
| P2 | Repo 配置技能 | T0449 | 初始化流程可运行 | 配置技能文件存在 |

## 改进计划与 PRD 验收条件对应

- **AC-3** ✅ 输出 P0/P1/P2 分级改进计划，6 项改进项均含关联任务/本体节点、验证方式和收敛条件（ev-improvement-plan-v1）
