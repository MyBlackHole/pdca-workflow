---
schema: pdca.asset/v1
id: ontology:domain/skill-design-it-twice
name: design-it-twice
summary: Design solutions twice to ensure robustness and catch edge cases.
description: |
  接口双方案设计。设计模块接口时并行产出 2 个以上根本不同的候选方案，
  用强制词汇表（module/interface/seam/adapter/depth）对比后给出推荐。
  使用场景：设计或重构任何带接口的模块、决定接缝位置、提升可测试性。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-design-it-twice/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/design-tree
    - ontology:concept/codebase-design
  testable_signal: "运行 grep -q 'ontology:domain/skill-design-it-twice' ontology/domain/pdca/skill-design-it-twice.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


-----|------|-------|
| **module** | 任何有接口与实现的单元（函数/类/包/跨层切片） | component, service |
| **interface** | 调用者使用模块所需的全部信息（类型签名+不变式+错误模式+配置） | API（过窄） |
| **seam** | 不编辑原地就能改变行为的位置；模块接口所在之处 | boundary |
| **adapter** | 在接缝处满足接口的具体实现，描述角色而非实质 | — |
| **depth** | 接口杠杆：每单位需学习的接口可驱动的行为量 | — |
| **leverage** | 调用者从深度获得的：每单位接口学习的更多能力 | — |
| **locality** | 维护者从深度获得的：变更/知识/验证集中于一处 | — |

一致性语言是整件事的意义所在——不要混用 component/service/API/boundary。

## 流程

### 1. 框定问题空间

写用户可读的问题空间说明（不产生方案）：
- 新接口必须满足的约束
- 依赖分类（in-process / local-substitutable / remote-owned / true-external）
- 让约束落地的示意代码草稿

展示给用户，随即进入步骤 2（用户在 sub-agent 并行工作时阅读思考）。

### 2. 并行产出方案

`agent.spawn` 可用时并行启动 2 个以上 sub-agent（不可用时主 session 顺序执行，
但保持方案彼此独立，不互相污染）。每个 sub-agent 分配**不同的设计约束**：

- Agent 1: "最小化接口——最多 1–3 个入口点，最大化每个入口点的杠杆"
- Agent 2: "最大化灵活性——支持多种用例与扩展"
- Agent 3: "为最常见调用者优化——让默认情形平凡化"
- Agent 4（如有）: "围绕端口与适配器设计跨接缝依赖"

每个 sub-agent 产出：
1. 接口（类型、方法、参数 + 不变式、顺序约束、错误模式）
2. 调用者如何使用它的示例
3. 实现藏在接缝后面的是什么
4. 依赖策略与适配器
5. 取舍——哪里杠杆高、哪里薄

sub-agent 的 brief 必须包含词汇表与 CONTEXT.md 词汇，确保命名一致。

### 3. 展示与对比

逐方案展示（让用户逐一吸收），再用散文对比。按三个维度：
- **depth**（接口处的杠杆）
- **locality**（变更集中于何处）
- **seam placement**（接缝位置）

对比后给出明确推荐（可提出混合方案）。要有主见——用户要的是强判断，不是菜单。

### 4. 词汇契约校验

设计产出文档经 `scripts/check-design-vocab.py` 校验：
- 通过（`vocab_ok: true`）→ 进入设计评审
- 违规（`vocab_ok: false`）→ 修正术语后重校验，违反即拒绝产出

## 深化测试策略（DEEPENING）

当候选是**浅模块集群**（多个 pass-through 聚集）时，先做深化评估再决定接口形状。
依赖分类已在上文步骤 1，这里给**确定性决策表**——依赖类别决定深化模块如何跨接缝测试：

| 依赖类别 | 判定 | 测试策略 | 是否需要 adapter |
|----------|------|----------|-----------------|
| **in-process** | 纯计算/内存态/无 I/O | 合并模块，直接经新接口测试 | 否 |
| **local-substitutable** | 有本地替身（PGLite/内存文件系统） | 用替身测；接缝内部，外部接口无 port | 否 |
| **remote-owned** | 自持服务跨网络（微服务/内部 API） | 接缝处定义 **port**，传输层注入为 **adapter**；测试用内存 adapter，生产用 HTTP/gRPC | 是 |
| **true-external** | 不可控第三方（Stripe/Twilio 等） | 外部依赖注入为 port，测试提供 mock adapter | 是 |

### seam 纪律

- **one adapter = 假设性接缝；two adapters = 真实接缝**。没有至少两个 adapter（通常生产 + 测试）不要引入 port——单 adapter 接缝只是间接层。
- **内部接缝 vs 外部接缝**：深模块可有内部接缝（实现私有，供自身测试用），但不要因测试使用就把内部接缝暴露到接口。

### deletion test（删减测试）

想象删除该模块：
- 复杂度**消失** → 它是 pass-through，不挣存在，应合并/删除。
- 复杂度**散布到 N 调用点** → 它在挣自己的存在，值得保留为深模块。

### replace, don't layer（替换而非叠加）

- 深化接口的测试一旦存在，浅模块的旧单测变**废物**——**删除**它们，不保留为叠加层。
- 新测试写在深化模块的**接口处**——**the interface is the test surface**。
- 测试断言接口外的**可观察结果**，不测内部状态。
- 测试应**挺过内部重构**：测试描述行为而非实现；若改实现需改测试，说明测过了接口。

## 与 code-review 的关系

design-it-twice 是设计阶段（Do E 路径前的方案生成），code-review 是审查阶段
（对已实现 diff 的双轴审查）。前者防锚定，后者防缺陷，不重叠。

## 完成

- 产出一个以上候选方案 + 对比 + 明确推荐
- 产出文档通过词汇契约校验（`vocab_ok: true`）
- 决策记录到 task 目录与 ADR（如不可逆）

## 已知坑

- 修改/新增 skill 后 `SKILLS-INDEX.md` 会过期，`test_generated_index_is_current` 捕获——用 `generate-skills-index.py` 重新生成（T0266 唯一真实回归）。
- DEEPENING 深化模块时，深化接口落地后浅模块旧单测变废物，须删除而非保留。


## 深模块词汇

设计时只使用 `codebase-design` 概念的词汇表：**module / interface / seam / adapter / depth / leverage / locality**。禁止 component/service/API/boundary。
