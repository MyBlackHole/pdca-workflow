# Research Report — 语义回链备选对比验证（T2114）

## 调研目标
验证候选B为何只能降级补充：事后回链能否证明事先具备。

## 方法
反例推演：超范围代码写入后仍可编造回链解释的情形。

## 发现
回链只能证明可解释性不能证明具备性；无声明锚点时解释可事后拼凑；B适合做A的补充审计。

### 回链缺口流程（mermaid）
```mermaid
flowchart TD
  A[超范围写入] --> B[事后编解释]
  B --> C{回链检查}
  C -- 通过 --> F[漏网]
  C -- 结合声明 --> P[被A拦截]
```
Source: records/T2112-0910-line-ontology-design/evidence/design.md

### 时序对比（mermaid）
```mermaid
sequenceDiagram
  participant A as 声明检查
  participant B as 回链审计
  participant C as 代码
  A->>C: 写前拦截
  C->>B: 写后审计
  B-->>C: 仅记录
```
Source: ontology:concept/scope-coverage-gate

### 定位状态机（mermaid）
```mermaid
stateDiagram-v2
  [*] --> 待定
  待定 --> 主方案: A事前
  待定 --> 补充审计: B事后
```
Source: https://lean.org/lexicon-terms/pdca

## 结论与建议
B降级为A的补充审计，不单独实施。

## 术语表
- 补充审计：事后记录不阻断

## 参考资料
- Source: https://lean.org/lexicon-terms/pdca
- Source: https://www.researchgate.net/publication/349440276_PDCA_Cycle_Method_implementation_in_Industries_A_Systematic_Literature_Review
