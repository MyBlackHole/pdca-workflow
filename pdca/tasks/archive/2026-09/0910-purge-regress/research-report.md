# Research Report — 删除回归验证迷你调研（T2129）

## 调研目标
确认删除前后失败集一致且提交可revert。

## 方法
stash对照全量失败集，diff仅少已删文件旧失败。

## 发现
前后51/56差集恰为已删文件5旧失败；stash污染工作区一次，已用checkout恢复。

### 回归对比流程（mermaid）
```mermaid
flowchart TD
  A[删后全量] --> B[失败集A]
  C[stash基线] --> D[失败集B]
  B --> E{diff==已删旧失败?}
  E -- 是 --> P[无回归]
  E -- 否 --> R[阻断提交]
```
Source: tests/test_operations.py

### 污染恢复时序（mermaid）
```mermaid
sequenceDiagram
  participant S as 基线运行
  participant W as 工作区
  participant P as pop
  S->>W: 测试污染health文件
  W->>P: checkout后pop
  P-->>W: 删件恢复
```
Source: records/T2127-0910-uncovered-scripts-purge/evidence/DELETION-MANIFEST.md

### 回归状态机（mermaid）
```mermaid
stateDiagram-v2
  [*] --> 待验
  待验 --> 可提交: 无新增失败
  待验 --> 回滚: 有新增失败
```
Source: https://lean.org/lexicon-terms/pdca

## 结论与建议
无回归，可提交。

## 术语表
- 差集：前后失败集合之差

## 参考资料
- Source: https://lean.org/lexicon-terms/pdca
- Source: https://www.researchgate.net/publication/349440276_PDCA_Cycle_Method_implementation_in_Industries_A_Systematic_Literature_Review
