---
schema: pdca.asset/v1
id: ontology:domain/skill-writing-great-skills
name: writing-great-skills
summary: Write great skills following the mattpocock/skills format.
description: 参考指南——如何编写和维护高质量的 PDCA 技能文件。定义了信息层级、极简原则、锚定词、指针措辞、双负载、完成判据杠杆、拆分规则和失败模式。SKILL-MECHANICS 定义 invocation 选择和 router 模式。
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/writing-for-agents
    - ontology:concept/domain-modeling
    - ontology:concept/leading-words
    - ontology:concept/pointer-wording
    - ontology:concept/no-op-judgment
    - ontology:concept/skill-mechanics
    - ontology:concept/skill-invocation-contract
    - ontology:concept/co-location
    - ontology:concept/context-pointer
    - ontology:concept/progressive-disclosure
---

# Writing Great Skills — PDCA 版

目标：**可预测性** — AI 每次执行同一技能时遵循同一过程。

## 信息层级

| 层级 | 位置 | 用途 |
|------|------|------|
| **步骤** | `SKILL.md` 顶部 | 按序执行的操作，每条有可检查完成标准 |
| **引用** | `SKILL.md` 靠后 | 定义、规则、事实 — 按需查阅 |
| **外部引用** | 独立 `.md` 文件 | 只有特定分支需要的细节，通过上下文指针加载 |

## 极简原则

1. **每行必须通过必要性测试**：去掉这行 AI 行为会变差吗？不会 → 删掉
2. **无操作不写**：AI 默认就会做的（"要全面"、"要仔细"）不写。如需约束用更强词（relentless > thorough）
3. **否定不如肯定**："不要 X" 不如 "做 Y"
4. **单点真实（SSOT）**：同一含义只在一个地方定义
5. **去沉积**：定期检查每个句子的相关性，不相关的立即删

## 锚定词（leading words）

用预训练已有的词锚定一类行为，重复以 **token** 而非句子，累积分布式定义并
招募模型已持有的先验：

- _tight_ → "快速、确定性、低开销"的紧凑反馈循环
- _red_ → "可证伪的失败信号"：模糊的门禁变成二值可观察状态（循环红了或没有）

- 自造词不招募先验——要用定义 token 偿还，优先改用已有词
- 出现三处同义短语指一概念 → 收拢为单 token
- 双赢：更少 token + 更锋利的触发钩子。每个文档都在携带可被锚定词退休的复述

## 指针措辞

上下文指针的**措辞**（非其目标）决定触发可靠性——目标再强，弱措辞就是方差 bug：
先改措辞，改不锋利才内联。

- **前置首词**：指针靠首词做触发工作
- **一分支一触发词**：同义改写=同一分支写两遍，收拢；只保留真正不同的分支
- 常载指针每轮花费 token，比正文更需狠修剪
- 正文已携带的身份信息，指针不再重复

## 双负载（two loads）

每个新增文档/指针花费两种预算之一：

- **context load**：常载材料每轮 token 成本（AGENTS.md 一行、技能描述、
  指针本身）——无论是否触发都在花
- **cognitive load**：人工索引成本——不是最小化对象，是人工判断权的代价，
  花在人工判断重要处，非判断处移除

渐进披露（推到指针后）主要不是 token 优化，是**保护信息层级**的手段。
判定：inline 每分支都要的；推指针只有某些分支达的。含步骤的文档若把
本应披露的引用留在文件内，会埋葬步骤、让"注意步骤"变成掷硬币。

## no-op 的模型相对判定

"无操作不写"（极简原则 2）的判定是**模型相对**的："这行是否改变默认行为"
取决于模型本身，不取决于读者。两人争论一句是否 no-op，实为争论默认行为——
用运行文档解决，不用辩论。

- 太弱的词是 no-op：_be thorough_ 当模型本就 thorough-ish → 换更强词
  （_relentless_），不是换技巧
- 失败时删整句，不删词——残句仍花 load 说无用的话

## user-invoked vs model-invoked

| | user-invoked | model-invoked |
|--|-------------|---------------|
| **标记** | `invocation: manual` | 无此标记 |
| **谁调用** | 仅用户打字 | AI 自动 + 用户均可 |
| **规则** | 可调用 model-invoked，不可调用其他 user-invoked | 描述需写清触发条件 |

## 何时拆分

| 场景 | 拆法 |
|------|------|
| 有独立触发词 | 拆为 model-invoked |
| 另一技能需调用它 | 拆为 model-invoked |
| 步骤太长导致 AI 想跳步 | 拆分步骤序列 |
| 内容是纯参考 | 推到外部引用 |

## 完成判据杠杆（completion criterion）

每步以"AI 如何分辨 done/not-done"收尾。两个独立性质，最强判据两者兼备：

- **clarity（防过早完成）**：模糊边界（"理解达成"）招致提前宣布完成——注意力滑向
  "已完成"状态，可见的后续步骤产生拉力，判据清晰度是阻力。两级防御按序用：
  先锐化边界（局部便宜）；不可约模糊**且观察到赶工**时才拆分序列隐藏后续步骤
  （仅在真实上下文边界有效：handoff 或子代理；inline 调用后继步骤仍在视野内，清不掉）。
- **demand（驱动 legwork）**："每个修改过的模型都被 accounted for"强制彻底工作，
  "产出变更清单"不能——demand 的挖掘量潜藏在措辞中而非写成独立步骤。
  demand 不限于步骤："每条规则都已应用"同样约束扁平引用体，这就是纯参考文档
  仍能携带穷尽性标准的机制。

好："所有 5 条证据都在 manifest 中登记且 digest 匹配"（可检验+穷尽）。
不好："完成证据登记"（无边界无 demand）。

## SKILL-MECHANICS

技能机制参考，定义三种核心机制：

1. **Invocation 选择**：model-invoked（省略 disable-model-invocation，AI 自动 + 用户均可）vs user-invoked（设 disable-model-invocation: true，仅用户打字）。user-invoked 不可调用其他 user-invoked。
2. **Splitting by invocation**：有独立触发词或另一技能需调用时拆为 model-invoked。
3. **Router skills**：user-invoked 技能过多时的路由模式，依赖通过 `Call the Skill tool with "name"` 显式表达。

详见 `ontology:concept/skill-mechanics` 和 `ontology:concept/skill-invocation-contract`。

## Cache 概念

Single source of truth 延伸到环境：`package.json` scripts、config 文件、目录布局、`--help` 输出本身就是权威。引用这些内容的文档是 lookups 的 cache，仅在 lookup 昂贵时才值得加载。

Positive target：cache agent 无法通过查看找到的内容（未写明的惯例、选择背后的原因、config 不肯承认的 gotcha）。将单文件、单命令的 lookups 留给环境。

**Cache 原则**：
- 环境即权威——`package.json` scripts、config 文件、目录布局、`--help` 输出是单点真实
- 不要在技能文档中重复环境已定义的内容
- 仅当 lookup 昂贵时才值得加载 cache
- Cache agent 无法通过查看找到的内容才是值得写的：未写明的惯例、选择背后的原因、config 不肯承认的 gotcha

## 失败模式

| 模式 | 修复 |
|------|------|
| 过早完成 | 完成判据杠杆：先锐化 clarity，仍赶工才拆分隐藏后续步骤 |
| 重复 | 合并到 SSOT |
| 沉积 | 定期逐行质问必要性 |
| 膨胀 | 将引用推到外部文件 |
| 无操作 | 用模型相对测试判定；删整句或换更强词（relentless > thorough） |
| 否定 | 改写为"做 Y" |
| 弱指针 | 前置首词 / 一分支一触发词 / 同义分支收拢 |
| 分散 | 概念的定义、规则、注意点同放一个标题下（co-location），散置≠重复 |
| 负空间（Negative Space）| 对"省略了什么"的 steering 视而不见；阅读草稿的沉默部分，逐个决定每个省略（填充或留作真实分支） |
| 缓存（Cache）| Single source of truth 延伸到环境——package.json scripts、config 文件、目录布局、--help 输出本身就是权威；cache agent 无法通过查看找到的内容 |

## Negative Space（负空间）

**Negative Space** 是对"省略了什么"的 steering。阅读草稿的沉默部分，逐个决定每个省略——是填充还是留作真实分支。

核心做法：
- **读草稿的沉默部分**：每个省略都是一个未做的决策
- **逐个决定**：填充内容或留作真实分支，不做沉默的省略
- **与 SSOT 互补**：Negative Space 关注的是"不在哪里"，SSOT 关注的是"在哪里"
- **验证方式**：对照 `ontology:concept/negative-space` 节点检查每个省略

## 已知坑

- 勿自造锚定词（不招募先验，需用定义 token 偿还）；否定约束转正向描述；同一含义保持单点真实（SSOT）。
- Negative Space 不可忽略——沉默的省略是最常见的知识缺口。