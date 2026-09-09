# 流程价值数据复盘

## 背景
用户判定流程已无使用价值。立项以度量裁决，避免感觉替代证据。

## 验收标准

- [ ] AC-1: 度量数据已采集，五维可复算
- [ ] AC-2: 价值与成本已判定，去留建议含阈值
- [ ] AC-3: 证据已登记，收敛valid:true

## 关联本体节点

```
ontology:domain/skill-retrospective
ontology:domain/skill-code-review
ontology:concept/self-optimization-loop
```

## 拆分映射

- 度量采集 -> ontology:domain/skill-retrospective
- 价值判定 -> ontology:domain/skill-code-review
- 闭环建议 -> ontology:concept/self-optimization-loop
