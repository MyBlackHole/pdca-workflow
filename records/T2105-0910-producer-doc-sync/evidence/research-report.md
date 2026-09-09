# Research Report — 简化方案方向调研（T2105）

## 调研目标
回答简化往哪走：比较统一证据入口、门禁合并、文档单点同步三方向。

## 方法
以每次门禁落地的三处同步（技能+流程+节点）为成本样本，评估合并收益。

## 发现
统一证据入口收益最大（一次登记多门引用）；门禁合并风险高（判定耦合）；文档单点同步可用门禁清单页实现。

### 方案比较流程（mermaid）
```mermaid
flowchart TD
  A[简化目标] --> B{统一入口?}
  B -- 是 --> P[收益大风险低]
  B -- 否 --> C{门禁合并?}
  C -- 是 --> Q[收益中风险高]
  C -- 否 --> R[文档单点]
```
Source: ontology:domain/skill-research

### 同步成本时序（mermaid）
```mermaid
sequenceDiagram
  participant D as 门禁落地
  participant S as 技能
  participant F as 流程
  participant O as 节点
  D->>S: 条款+1
  D->>F: 步骤内联+1
  D->>O: 属性+1
```
Source: ontology/process/flow-do.md

### 方案状态机（mermaid）
```mermaid
stateDiagram-v2
  [*] --> 待选
  待选 --> 统一入口: 推荐
  待选 --> 门禁合并: 高风险
  待选 --> 文档单点: 保底
```
Source: https://lean.org/lexicon-terms/pdca

## 结论与建议
推荐统一入口立项前先小步验证；本任务只调研不定案。

## 术语表
- 单点：文档修改收敛到一处

## 参考资料
- Source: https://lean.org/lexicon-terms/pdca
- Source: https://www.researchgate.net/publication/349440276_PDCA_Cycle_Method_implementation_in_Industries_A_Systematic_Literature_Review
