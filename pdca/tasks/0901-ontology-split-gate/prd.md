# 拆分门禁硬化

## 背景
当前 `to-tickets#3.5` 仅在 PRD 含拆分映射且有 fragment 时触发，默认静默跳过，clash-check 虽阻断但误报多。

## 目标
使本体对齐成为默认路径，有 fragment 即跑 tree_split，无映射告警不静默，clash-check 保持阻断，task_identity 继承强化。

## 功能需求
1. `skill-to-tickets.md` 3.5 由可选改为默认：有 `meta.ontology_fragment` 即执行 `ontology_tree_split`，无 `## 拆分映射` 时告警并回退章节拆分
2. 保留 `ontology-clash-check` 阻断，但支持声明复用（PRD 已列关联本体时提示而非硬失败）
3. `task_identity.py` 继承 fragment/node_type 已具备，需文档与测试可视化

## 非功能
- 兼容旧任务：无 fragment 仍走章节拆分
- 门禁可观测：tree_split 输出 candidates 机器可读

## 验收标准
- [ ] AC-1 拆分默认：有 fragment 时 `ontology_tree_split` 必跑，无映射告警回退，clash-check 阻断保留
- [ ] AC-2 继承生效：子任务自动继承父 `ontology_fragment/node_type`，无需手工传参

## 关联本体节点
```
ontology:entity/ontology-deep-integration-split
ontology:pattern/ontology-modular-reference
ontology:domain/ai-efficiency-ticket-dag-ready-set
```

## 拆分映射
- 拆分门禁硬化 -> ontology:entity/ontology-deep-integration-split
