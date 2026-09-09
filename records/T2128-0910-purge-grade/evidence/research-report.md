# Research Report — 分级裁决方法迷你调研（T2128）

## 调研目标
固定分级裁决四步：候选计算、精确耦合扫描、调用方确认、分级保留。

## 方法
复盘本次25/35裁决过程，记录每级保留理由。

## 发现
运行时导入与kept调用为硬保留；测试连带须看排他性；他人在途以未跟踪与近期提交判定。

### 裁决流程（mermaid）
```mermaid
flowchart TD
  A[候选] --> B{运行时导入?}
  B -- 是 --> K[保留]
  B -- 否 --> C{测试排他?}
  C -- 是 --> P[连带删]
  C -- 否 --> D[剪方法]
```
Source: scripts/transition-phase.py:19-21行

### 保留核验时序（mermaid）
```mermaid
sequenceDiagram
  participant R as 裁决
  participant I as import扫描
  participant K as 保留项
  R->>I: 精确匹配非子串
  I-->>R: X4+resolve×2+CI链
```
Source: ontology/concept/process-complexity-ruling.md

### 裁决状态机（mermaid）
```mermaid
stateDiagram-v2
  [*] --> 待判
  待判 --> 保留: 硬耦合
  待判 --> 删除: 孤儿确认
```
Source: https://lean.org/lexicon-terms/pdca

## 结论与建议
方法可复用，后续purge照此四步。

## 术语表
- 硬耦合：删即破坏运行或测试

## 参考资料
- Source: https://lean.org/lexicon-terms/pdca
- Source: https://www.researchgate.net/publication/349440276_PDCA_Cycle_Method_implementation_in_Industries_A_Systematic_Literature_Review
