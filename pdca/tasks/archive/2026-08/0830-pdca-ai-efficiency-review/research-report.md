# PDCA 本体与 Matt Pocock skills 对比审查

**任务**: T0430 审查 PDCA 本体是否符合提升 AI 使用效率，借鉴 Matt Pocock skills
**研究日期**: 2026-08-30
**场景**: research

## 审查方法

1. 获取 Matt Pocock skills 仓库核心技能定义
2. 逐一对比 PDCA 本体（ontology/concept/）中的概念节点
3. 识别缺失的概念和原则
4. 评估现有技能（skills/）对 Matt Pocock 原则的覆盖度

## Matt Pocock 核心原则

### 1. Writing for Agents（为 Agent 写作）
- **信息层级**（Information Hierarchy）：步骤 → 文件中引用 → 披露引用
- **渐进披露**（Progressive Disclosure）：将引用推到指针后方
- **上下文指针**（Context Pointer）：命名出域外材料及其触发条件
- **步骤 + 完成标准**（Steps + Completion Criteria）：每个步骤以完成条件结束
- **共置**（Co-location）：概念的定义、规则、注意事项放在同一标题下
- **两种负载**：上下文负载（context load）与认知负载（cognitive load）

### 2. Skill Mechanics（技能机制）
- **模型调用 vs 用户调用**（Model-invoked vs User-invoked）
- **路由技能**（Router Skills）：一个用户调用技能命名其他技能及触发时机
- **共享引用**（Shared Reference）

### 3. Grilling（追问方法论）
- **设计树**（Design Tree）：每个决策分支为下游决策
- **前沿**（Frontier）：所有前置已确定的决策
- **轮次**（Rounds）：每轮询问整个前沿
- **事实而非观点**（Facts Not Opinions）
- **完成标准**（Completion Criteria）：前沿为空时会话结束

### 4. Domain Modeling（领域建模）
- **活跃纪律**（Active Discipline）：讨论代码时积极构建领域模型
- **挑战术语表**（Challenge Glossary）
- **模糊语言精确化**（Sharpen Fuzzy Language）
- **AGENT-BRIEF.md**：持久的 Agent 简要

### 5. Triage（分诊）
- **状态机**（State Machine）：triage 角色状态机
- **Agent 就绪简要**（Agent-Ready Briefs）
- **AI 免责声明**（AI Disclaimer）

### 6. To Tickets（任务拆分）
- **垂直切片**（Vertical Slices）：每个切片穿过每一层
- **追踪弹**（Tracer Bullets）：小而完整的垂直切片
- **阻塞边**（Blocking Edges）：其他必须完成的票
- **展开-收缩**（Expand-Contract）：宽重构的序列策略

## PDCA 现状分析

### 已有概念（43 个）

| 类别 | 概念节点 |
|------|----------|
| PDCA 核心 | pdca, pdca-phase, pdca-task, pdca-gate, pdca-gate-do, pdca-ontology-ready, pdca-transition, pdca-verdict, pdca-evidence, pdca-acceptance-criterion, pdca-architecture, pdca-ai-friendly-confirmation, pdca-scenario-boundary-rule, pdca-source-diagram-doc-verification, pdca-architecture-review-metrics, pdca-provable-skill-increments, pdca-home, pdca-continuous-improvement |
| 流程 | process, flow-plan, flow-do, flow-check, flow-act, code-review-process |
| 实体 | entity, domain-entity, knowledge-artifact, knowledge-provenance, task-record-identity, timeline-integrity-gate |
| 事实 | fact |
| 模式 | pattern |
| 陷阱 | pitfall |
| 原则 | principle |
| 本体规则 | ontology-rule, ontology-validate, ontology-creation-gate, ontology-rule-acyclic, ontology-rule-non-dangling, ontology-rule-type-controlled, ontology-rule-guides-range, ontology-rule-richness, ontology-rule-attr-testable |
| 其他 | capability-protocol, executor-adapter, external-evidence-collection, destructive-cleanup-safety, self-optimization-loop, runtime-transition-coordinator, real-project-mechanism-validation, meta-ontology |

### 缺失概念分析

#### 1. Writing-for-agents 原则 → 完全缺失

| Matt Pocock 原则 | PDCA 对应 | 状态 |
|------------------|-----------|------|
| 信息层级（步骤/文件中引用/披露引用） | 无 | ❌ 缺失 |
| 渐进披露 | 无 | ❌ 缺失 |
| 上下文指针 | 无 | ❌ 缺失 |
| 步骤 + 完成标准 | pdca-task 无 steps/criteria 字段 | ❌ 缺失 |
| 共置 | 无 | ❌ 缺失 |
| 两种负载（context load / cognitive load） | 无 | ❌ 缺失 |

#### 2. Skill Mechanics → 完全缺失

| Matt Pocock 原则 | PDCA 对应 | 状态 |
|------------------|-----------|------|
| 模型调用 vs 用户调用 | pdca-provable-skill-increments 仅记录增量，未区分调用方式 | ⚠️ 部分 |
| 路由技能 | 无 | ❌ 缺失 |
| 共享引用 | 无 | ❌ 缺失 |

#### 3. Grilling 方法论 → 完全缺失

| Matt Pocock 原则 | PDCA 对应 | 状态 |
|------------------|-----------|------|
| 设计树 | 无 | ❌ 缺失 |
| 前沿 | 无 | ❌ 缺失 |
| 轮次 | 无 | ❌ 缺失 |
| 事实而非观点 | grilling skill 中有类似描述，但无本体概念 | ⚠️ 部分 |
| 完成标准 | 无 | ❌ 缺失 |

#### 4. Domain Modeling → 完全缺失

| Matt Pocock 原则 | PDCA 对应 | 状态 |
|------------------|-----------|------|
| 活跃纪律 | 无 | ❌ 缺失 |
| 挑战术语表 | 无 | ❌ 缺失 |
| 模糊语言精确化 | 无 | ❌ 缺失 |
| AGENT-BRIEF.md | 无 | ❌ 缺失 |
| CONTEXT.md 等价物 | 无 | ❌ 缺失 |

#### 5. Triage → 完全缺失

| Matt Pocock 原则 | PDCA 对应 | 状态 |
|------------------|-----------|------|
| 状态机 | 无 | ❌ 缺失 |
| Agent 就绪简要 | 无 | ❌ 缺失 |
| AI 免责声明 | 无 | ❌ 缺失 |

#### 6. To Tickets → 完全缺失

| Matt Pocock 原则 | PDCA 对应 | 状态 |
|------------------|-----------|------|
| 垂直切片 | 无 | ❌ 缺失 |
| 追踪弹 | 无 | ❌ 缺失 |
| 阻塞边 | 无 | ❌ 缺失 |
| 展开-收缩 | 无 | ❌ 缺失 |

### 技能引用缺失的本体概念

| 技能 | 引用的缺失概念 |
|------|---------------|
| ontology-check | ontology:concept/ontology-creation-gate, ontology:concept/ontology-rule-* |
| register-evidence | ontology:concept/pdca-evidence（短名引用） |

## 改进建议

| # | 严重度 | 类别 | 描述 | 建议 |
|---|--------|------|------|------|
| 1 | major | 信息层级 | PDCA 本体缺少信息层级概念 | 添加 `ontology:concept/information-hierarchy` 及子概念 |
| 2 | major | 技能机制 | PDCA 本体缺少模型调用 vs 用户调用 | 添加 `ontology:concept/skill-invocation` 及子概念 |
| 3 | major | 追问方法论 | PDCA 本体缺少设计树、前沿、轮次 | 添加 `ontology:concept/grilling-methodology` 及子概念 |
| 4 | major | 领域建模 | PDCA 本体缺少 CONTEXT.md 等价物 | 添加 `ontology:concept/domain-model` 及子概念 |
| 5 | major | 分诊 | PDCA 本体缺少状态机、Agent 就绪简要 | 添加 `ontology:concept/triage` 及子概念 |
| 6 | major | 任务拆分 | PDCA 本体缺少垂直切片、追踪弹、阻塞边 | 添加 `ontology:concept/task-decomposition` 及子概念 |
| 7 | medium | 路由技能 | PDCA 本体缺少路由技能 | 添加 `ontology:concept/router-skill` |
| 8 | medium | 共享引用 | PDCA 本体缺少共享引用 | 添加 `ontology:concept/shared-reference` |
| 9 | medium | AGENT-BRIEF | PDCA 本体缺少 AGENT-BRIEF 概念 | 添加 `ontology:concept/agent-brief` |
| 10 | low | 渐进披露 | PDCA 本体缺少渐进披露 | 添加 `ontology:concept/progressive-disclosure` |

## 结论

PDCA 本体在核心流程（plan/do/check/act）和本体规则方面已较完善，但在与 Matt Pocock skills 对齐的 AI 使用效率原则方面存在显著缺口：

- **6 大类原则完全缺失**：信息层级、技能机制、追问方法论、领域建模、分诊、任务拆分
- **pdca-task 缺少 steps 和 completion criteria 字段**
- **技能引用了 3 个缺失的本体概念**：ontology-creation-gate、ontology-rule-*、pdca-evidence

建议优先补充信息层级、技能机制和追问方法论的概念节点，以提升 PDCA 本体对 AI 使用效率的支撑能力。
