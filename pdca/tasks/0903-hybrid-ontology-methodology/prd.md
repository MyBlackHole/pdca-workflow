# 沉淀混合方法论本体并应用：调研顶向下与开发底向上双向

## 背景

T0494前网络核验：Ontology101(top-down/bottom-up/combination)、METHONTOLOGY(evolving prototype)、NeOn 9场景、WBS(100% Rule/Yo-Yo hybrid)、DDD bounded context 三支正交方法论共同支撑本地“调研根→叶全面记录、开发叶→根实现、叶子可独立验证”实践。需将该混合方法论显式沉淀为本体（可复用、可校验），并立即以 `report-center-system` 根实体为示范应用，验证叶→根与粒度门禁。

## 目标

- 沉淀 `ontology/domain/ontology-hybrid-methodology.md`（根）`composed_of` 3子：`research-topdown` / `develop-bottomup` / `leaf-granularity-middleout`
- 三子各含 `attributes.testable_signal` 三模式可派生，且可 `scaffold`
- 以 `report-center-system(composed_of: web, collection)` 为应用示范，叶粒度满足三准绳且 `tree_split` 可调度

## 范围

- 输入：Stanford Ontology101、METHONTOLOGY 1997、NeOn 2012、PMI WBS、DDD
- 输出：1根+3叶共4节点 + 1示范应用校验 + 全绿
- 不做：不改全量365 nodes结构，不新增业务代码

## 功能需求

1. 根本体：`ontology-hybrid-methodology` 3 `composed_of` 子，关系可经 `ontology_graph` 追溯
2. Research Topdown：描述 根→叶 全面记录、100% Rule、中层显著概念优先
3. Develop Bottomup：描述 叶→根 `dependencies` + `ready-set [[叶],[根]]` + Work Package可分配
4. Leaf Middle-out：描述 可独立验证/演进/复用 三准绳与粒度失衡修复（过粗split/过细merge）
5. 应用：`report-center-system` 2叶满足三准绳且 `python3 scripts/ontology_tree_split.py --ontology-dir ontology --prd <demo-prd>` 可产候选

## 非功能需求

- `ontology-validate 0 issues, islands:0`，`scaffold` 可产4节点骨架

## 验收标准

- [ ] AC-1 根+3叶已创建且 `ontology-validate` 通过且 `composed_of` 3边可 `graph` 追溯
- [ ] AC-2 三子各 `attributes.testable_signal` 非空且可 `scaffold`（`ontology_test_scaffold --node` 可产）
- [ ] AC-3 应用示范：`report-center-system` 2叶满足三准绳且 `tree_split` 可调度
- [ ] AC-4 索引与图谱：`SKILLS-INDEX` 重生成且 `islands:0`
- [ ] AC-5 收敛 valid:true

## 关联本体节点

```
ontology:domain/ontology-hybrid-methodology
ontology:domain/ontology-hybrid-research-topdown
ontology:domain/ontology-hybrid-develop-bottomup
ontology:domain/ontology-hybrid-leaf-middleout
ontology:entity/report-center-system
```

## 拆分映射

- 根与Research Topdown -> ontology:domain/ontology-hybrid-research-topdown
- Develop Bottomup -> ontology:domain/ontology-hybrid-develop-bottomup
- Leaf Middle-out -> ontology:domain/ontology-hybrid-leaf-middleout
- 应用示范 -> ontology:entity/report-center-system
