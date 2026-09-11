# PDCA流程本体优化空间调研（T2153）

## 背景

流程本体经多轮审查与落地（T2135/T2148/T2152），仍有已知未立项项。
本次全库扫描，系统性回答是否有优化空间。

## 范围

全库：流程核心（pdca/flow-*/门禁/任务机制）+ 领域子树抽样 + 执行链抽查。

## 方法

结构维（孤岛/悬空/环/版本）+ 语义维（重复/漂移/缺口：role/待补、AC-5、退役机制）
+ 机制维（门禁覆盖：transition 依赖校验、ci 悬空引用、双层闸 bugfix）。

## 验收标准

- [ ] AC-1: research-report 通过门禁（mermaid≥3/Source≥3/http Source≥1/URLs≥2）
- [ ] AC-2: 优化空间清单分级（P0/P1/P2 含影响与依据）
- [ ] AC-3: 结构类附带修订验证通过，语义类有改进候选或无优化结论

## 关联本体节点

```
ontology:concept/pdca
ontology:process/flow-plan
ontology:process/flow-do
ontology:process/flow-check
ontology:process/flow-act
```

## 拆分映射

- 全库扫描执行 -> ontology:concept/pdca
- 报告与修订 -> ontology:process/flow-do
