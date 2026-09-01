# Act知识闭环收紧：disposition节点校验与archive硬门禁

## 背景
现 `ontology_gate` 仅关键词检 `ontology:`，未验节点存在性；`records-only` 未验 evidence 非空。

## 目标
Act从字符串含 `ontology:` 升级为节点存在性+`validate`+`islands:0` 硬门禁。

## 功能需求
1. `meta.disposition.reason` 中 `ontology:xxx` 须确为 `ontology/<type>/*.md` 且 `pdca.asset/v1` 合法，否则 `transition-phase.py → archive` 拒收
2. `records-only` 时 `records/<record>/evidence/manifest.jsonl` 非空，否则拒收
3. 伪串/空evidence给出可执行 `guidance`

## 验收标准
- [ ] AC-1 伪 `ontology:xxx` 在 archive 被 `DISPOSITION_ONTOLOGY_NOT_FOUND` 拒收
- [ ] AC-2 `records-only` 无 evidence 时 `DISPOSITION_RECORDS_ONLY_EMPTY` 拒收，真节点放行


## 关联本体节点
```
ontology:entity/ontology-deep-integration-knowledge
ontology:concept/ontology-validate
ontology:concept/pdca-task
```

## 风险与对策
- 风险：历史任务被误拦。对策：仅对 `phase ∈ check/act/archive` 且含 `disposition` 的新任务生效
