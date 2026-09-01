# 树形执行与依赖推导

## 背景
`composed_of` 仅 TLS/transition 等少数有，领域层多为 specializes 分类，WBS 树不饱满，叶→根调度仅 ready-set 文本无可视。

## 目标
补齐核心 `composed_of` 边，使 tree_split 能叶→根派生 dependencies，ready-set 可视化。

## 功能需求
1. 为本次 5 实体已补齐 `composed_of`（父聚合4叶），并示范为 ReportCenter 或其他一域补一条 `composed_of` 示例（可选）
2. 验证 `compute-frontier.py` 对拆分后 DAG 输出 `valid:true` 且 `batches` 体现叶并行根串行
3. 提供 `ontology_graph --format dot` 导出树图，写入 PRD 附录或 `docs/wbs.dot`

## 非功能
- 不违 `COMPOSED_OF_RANGE`（目标仅 entity/concept）
- 保持 `islands:0`

## 验收标准
- [ ] AC-1 叶→根依赖：`ontology_tree_split` 对本任务输出5候选，根依赖4叶
- [ ] AC-2 可调度与可视：`compute-frontier` batches 为 [[叶集],[根]]，`dot` 含4条 composed_of 边

## 关联本体节点
```
ontology:entity/ontology-deep-integration-tree
ontology:entity/ontology-deep-integration
ontology:domain/ai-efficiency-ticket-dag-ready-set
```

## 拆分映射
- 树形执行与依赖推导 -> ontology:entity/ontology-deep-integration-tree
