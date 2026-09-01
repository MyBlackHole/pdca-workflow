# 全任务知识闭环

## 背景
仅 research 强制知识沉淀，其余 scenario 可空 fragment 通关，Act disposition 无本体关键词亦可归档，导致知识断链。

## 目标
实现无任务不知识：任意任务可通过本体表达，Act 强制沉淀。

## 功能需求
1. 更新 `ontology/process/flow-act.md` 与 `ontology_gate.auto_induce_evidence`：Act 要求 `meta.disposition` 含 `ontology:` 或显式 `records-only` + 理由，否则 `archive` 门禁拒收（顾问式提示升级为硬校验可选）
2. 确认 `meta.ontology_anchor` 默认 `ontology:concept/pdca-task`，任意任务可声明 `fragment` 挂本体
3. 在 `skill-to-tickets` 与 `flow-do` 文档中明确全任务闭环声明位置

## 非功能
- 历史任务不追溯，仅新任务生效
- `auto_induce` 提示可执行命令

## 验收标准
- [ ] AC-1 任意任务可表达：新建 development/bugfix/research 各一，声明不同 fragment 均通过 `ontology-ready`
- [ ] AC-2 强制沉淀：无本体关键词的 disposition 在 `act→archive` 被 `ontology_gate` 拒收，有关键词通过

## 关联本体节点
```
ontology:entity/ontology-deep-integration-knowledge
ontology:concept/knowledge-provenance
ontology:concept/pdca-task
ontology:process/flow-act
```

## 拆分映射
- 全任务知识闭环 -> ontology:entity/ontology-deep-integration-knowledge
