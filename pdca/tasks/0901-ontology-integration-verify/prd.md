# 集成验证与回归

## 背景
4叶完成后需集成验证，确保门禁全绿且收敛闭环可验证。

## 目标
端到端演练，输出全绿报告与证据链。

## 功能需求
1. 运行 `ontology-validate`、`ontology_graph --format summary`、`compute-frontier` 对父任务 DAG、`validate-convergence` 对各子任务
2. 生成 `records/<record>/evidence` 登记，含 validate/graph/frontier/convergence 全量产物，登记为 evidence
3. 更新日志 `pdca/journal/YYYY-MM-DD.md` 与本体总览关联

## 非功能
- 全自动化脚本一键回归

## 验收标准
- [ ] AC-1 全绿：`validate` 0 issues，`graph` islands:0，`frontier` valid:true
- [ ] AC-2 收敛：`validate-convergence` 对 T0471 valid:true 且每条 AC 有非 map evidence 覆盖
- [ ] AC-3 链路可控：单任务引用本体数≤3，清单透传不单独立节点

## 关联本体节点
```
ontology:entity/ontology-deep-integration
ontology:domain/ontology-deep-integration-overview
ontology:pattern/ontology-modular-reference
```

## 拆分映射
- 集成验证与回归 -> ontology:entity/ontology-deep-integration
