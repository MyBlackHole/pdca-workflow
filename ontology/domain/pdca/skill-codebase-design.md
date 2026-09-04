---
schema: pdca.asset/v1
id: ontology:domain/skill-codebase-design
name: codebase-design
summary: 深模块设计纪律——用 module/interface/seam/adapter/depth 词汇构建可维护的深模块
description: |
  深模块设计纪律：为代码库建立精确的架构词汇（module/interface/seam/adapter/depth/leverage/locality），
  让 agent 在讨论代码结构时零歧义。使用场景：设计或重构任何带接口的模块、决定接缝位置、提升可维护性。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-codebase-design/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/design-tree
    - ontology:concept/domain-modeling
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# Codebase Design — PDCA 版

深模块设计纪律：为代码库建立精确的架构词汇，让 agent 在讨论代码结构时零歧义。

## 词汇表（契约）

只使用以下术语，禁止通用词：

| 术语 | 含义 | 禁用词 |
|------|------|--------|
| **module** | 任何有接口与实现的单元（函数/类/包/跨层切片） | component, service |
| **interface** | 调用者使用模块所需的全部信息（类型签名+不变式+错误模式+配置） | API（过窄） |
| **seam** | 不编辑原地就能改变行为的位置；模块接口所在之处 | boundary |
| **adapter** | 在接缝处满足接口的具体实现，描述角色而非实质 | — |
| **depth** | 接口杠杆：每单位需学习的接口可驱动的行为量 | — |
| **leverage** | 调用者从深度获得的：每单位接口学习的更多能力 | — |
| **locality** | 维护者从深度获得的：变更/知识/验证集中于一处 | — |

## 深模块原则

1. **深模块优先**：大量行为通过简单接口暴露，而非暴露大量细节
2. **接口即契约**：interface 定义了调用者与模块之间的全部约定
3. **seam 即灵活性**：每个 seam 是一个可以替换 adapter 的位置
4. **depth 即效率**：深度越大，每单位接口学习的行为越多
5. **locality 即可维护性**：变更集中在少数位置

## 设计流程

1. **识别 module**：确定要设计的模块边界
2. **定义 interface**：声明 module 的完整接口（类型签名+不变式+错误模式+配置）
3. **定位 seam**：找到可以不编辑原地就改变行为的位置
4. **选择 adapter**：为每个 seam 选择或实现 adapter
5. **评估 depth**：检查接口的 leverage 和 locality

## 与相关技能的关系

- `design-it-twice`：用强制词汇表对比双方案
- `improve-codebase-architecture`：扫描代码库深化机会
- `domain-modeling`：构建共享语言
- `to-spec`：将设计转化为 spec

## AI 效率机制

- 精确词汇消除 agent 的歧义猜测
- 模块/接口/seam 词汇让架构讨论可验证
- depth/leverage/locality 提供量化评估维度
- 词汇表约束（禁用通用词）强制精确表达

## 已知坑

- 词汇表约束是契约测试的守护对象，不守护"用法正确"
- 跨模型族（如中文模型）先验词不同，需本地验证
- seam 过多（过度分隔）会降低 depth
