# Research Report — 门禁实现与测试设计调研（T2094）

## 调研目标
确定先调研门禁的代码落点与测试覆盖：放`gate_issues` plan分支，5例覆盖阻断/放行/豁免/自指。

## 方法
走读门禁调用链与豁免条件，复用既有TICKETS测试夹具模式。

## 发现
落点选`gate_issues`可复用任务schema校验与澄清ledger；索引扫描限定`pdca/tasks`递归，失败闭环不抛异常。

### 门禁流程（mermaid）
```mermaid
flowchart TD
  A[gate_issues plan分支] --> B{ontology_exempt?}
  B -- 是 --> P[跳过]
  B -- 否 --> C{报告通过?}
  C -- 是 --> P[放行]
  C -- 否 --> D{链内归档research?}
  D -- 是 --> P
  D -- 否 --> R[RESEARCH_FIRST_MISSING]
```
Source: scripts/pdca_core.py 先调研门禁段

### TDD时序（mermaid）
```mermaid
sequenceDiagram
  participant T as 测试
  participant G as 门禁
  T->>G: 无证据dev进门禁
  G-->>T: 阻断红灯
  T->>G: 补实现后重跑
  G-->>T: 5例全绿
```
Source: tests/test_research_first_gate.py

### 豁免状态机（mermaid）
```mermaid
stateDiagram-v2
  [*] --> 核验中
  核验中 --> 豁免: ontology_exempt
  核验中 --> 放行: 证据二选一成立
  核验中 --> 阻断: 无证据无豁免
```
Source: https://lean.org/lexicon-terms/pdca

## 结论与建议
落点与用例完备，自指用例锁定待升级行为。

## 术语表
- 红绿：先失败测试后最小实现

## 参考资料
- Source: https://lean.org/lexicon-terms/pdca
- Source: https://www.researchgate.net/publication/349440276_PDCA_Cycle_Method_implementation_in_Industries_A_Systematic_Literature_Review
