---
schema: pdca.asset/v1
id: ontology:domain/skill-domain-modeling-work
name: domain-modeling-work
summary: Domain modeling work for understanding business logic.
description: Maintain the shared project language and ADRs while planning or executing work.
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-domain-modeling-work/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


--
name: domain-modeling-work
description: Maintain the shared project language and ADRs while planning or executing work.
---

# 领域建模工作

## 核心原则
- **即时落地**：只要一个术语被澄清，立即编辑 `$PDCA_HOME/pdca/CONTEXT.md`，不批量处理。
- **不假定已知**：每次遇到模糊术语，先对照现有 CONTEXT.md 检查，再提问确认。
- **硬决策必有记录**：不可逆、非显然、有权衡的决策必须写入对应 `ontology/` 节点（加「决策背景」段）。

## 术语管理

### 识别模糊术语
- 用户在描述需求时用了含混的词汇（"模块""组件""接口""服务""系统"）
- 不同上下文下含义不同的词（"用户""权限""策略""配置"）
- 团队内部自创但无明确定义的缩略语

### 流程
1. 问："你说的 'X' 具体是指什么？"
2. 确认定义后，打开 `$PDCA_HOME/pdca/CONTEXT.md`，在 `# 术语表` 章节追加 `## X` + 定义
3. 查阅现有术语：直接读取 `$PDCA_HOME/pdca/CONTEXT.md`
4. 搜索已有术语：用 grep 搜索 `$PDCA_HOME/pdca/CONTEXT.md`

### CONTEXT.md 格式约定

```markdown
# 术语表

## <术语名>
<定义，可多行>

## <另一个术语>
<定义>
```

### 术语质量要求
- 清晰区分类/实例关系（"用户" vs "当前登录用户"）
- 边界明确（"不包括 Y")
- 与代码中的命名一致（如有冲突，指出差异）

## ADR 管理

### 何时记录 ADR
满足以下任意条件时建议记录：
- 两个方案都有合理论据，最终选择了其中一个
- 决策影响后续多个任务
- 决策涉及架构级别的变化
- 决策有明确的 constrain（成本、时间、技术栈）

### 决策节点格式（对应 `ontology/concept/<slug>.md`，pdca.asset/v1 frontmatter）

```
# ADR-NNNN: 标题
日期: YYYY-MM-DD
状态: Proposed | Accepted | Deprecated | Superseded

## 背景
决策上下文和动机。

## 决策
最终选择了什么方案，为什么。

## 影响
采纳此决策的后果和权衡。
```

### 流程
1. 确认背景和上下文
2. 列出至少两个候选方案及其权衡
3. 在 `ontology/` 中新建/扩展对应概念节点承载该决策（不再使用 ADR 文件）。
4. 查看已有决策：检索 `ontology/` 节点。
5. 查看某条 ADR：读取对应文件

## 与 Grill 的协作关系
Grill 是提问引擎，domain-modeling-work 是知识沉淀层。
每个 grill session 结束后应当报告：
- 新增/更新了哪些术语
- 是否记录了新的 ADR

## 已知坑

- 术语变更须同步 `pdca/CONTEXT.md`；架构级硬决策须沉淀进 `ontology/` 节点，只改 skill 不落记录会导致漂移。
