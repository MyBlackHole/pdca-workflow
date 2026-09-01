# 生产本体方法论深化：面面俱到补全至可独立指导

## 背景

T0495混合方法论4节点仅骨架（每节点2 attrs、3行正文），对照 `ontology-modular-reference:116` 与 `testable-signal:89` 的“面面俱到”标准，缺约束阈值、验收用例、反模式、PDCA对接、命令示例。新节点无法独立指导“调研根→叶→开发叶→根”全链，需深化至生产可用。

## 目标

- 4节点各扩至 ≥3 attrs（含约束/阈值/反例）、正文≥60行（含决策树/正反例/门禁衔接/命令）
- 单节点即可独立派生 `tree_split`/`scaffold`/`frontier`，无需外查

## 范围

- 输入：T0495 4节点、`modular-reference` `testable-signal` 详细范式
- 输出：4节点深化版 + `ontology-validate` `graph islands:0` + `scaffold 4节点可产`
- 不做：不新增节点，不改业务实体结构

## 功能需求

1. hybrid-methodology：补 `research_completeness` `develop_assignability` `leaf_governance` 3 attrs，附决策树与100%检验命令
2. research-topdown：补 `100% Rule` 用例、`middle-out` 正反例、`flow-plan/do` 对接
3. develop-bottomup：补 `Work Package` 分配清单、`ready-set` 并行度、`flow-do/act` 对接
4. leaf-middleout：补 三准绳量化阈值（≥2复用/≥3 attrs/正交） + 过粗/过细反模式 + Yo-Yo修复命令

## 非功能需求

- 每节点 `attributes ≥3` 且 `testable_signal` 三模式可派生，`bash -n` 与 `scaffold` 可产

## 验收标准

- [ ] AC-1 hybrid-methodology深化：≥3 attrs且含决策树，validate通过
- [ ] AC-2 research-topdown深化：含100%与middle-out正反例，scaffold可产
- [ ] AC-3 develop-bottomup深化：含Work Package与ready-set，scaffold可产
- [ ] AC-4 leaf-middleout深化：含三准绳阈值与反模式，scaffold可产
- [ ] AC-5 全量校验：`ontology-validate 0 issues, islands:0, 4节点均scaffold可产` 且 `SKILLS-INDEX` 一致
- [ ] AC-6 收敛 valid:true

## 关联本体节点

```
ontology:domain/ontology-hybrid-methodology
ontology:domain/ontology-hybrid-research-topdown
ontology:domain/ontology-hybrid-develop-bottomup
ontology:domain/ontology-hybrid-leaf-middleout
```

## 拆分映射

- 根深化 -> ontology:domain/ontology-hybrid-methodology
- 三叶深化 -> ontology:domain/ontology-hybrid-research-topdown
- 应用补全 -> ontology:domain/ontology-hybrid-leaf-middleout
