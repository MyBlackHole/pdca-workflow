# 复用检索与clash联动：相似本体推荐与强引用

## 背景
新建任务与本体重名仅靠 `clash-check` 字面命中，无相似度推荐与扇出校验。

## 目标
候选slug在 `clash-check` 前经图谱检索相似本体，提示复用边，`relations` 强引用可被 `validate`/`graph` 追溯。

## 功能需求
1. 候选经 `ontology_graph --format summary` 检索字面/relations 相似本体，输出 `ontology:xxx` 复用建议
2. 推荐边写入 `relations: relates_to/guides` 强引用，非文本提及
3. `ontology-validate` AC-5/AC-6 对强引用可追溯，`islands` 不增

## 验收标准
- [ ] AC-1 `ontology-clash-check` 对近似既有节点阻断并提示 `ontology:xxx` 复用
- [ ] AC-2 推荐边为 `relations` 强引用且可被 `ontology-validate` 与 `ontology_graph` 追溯


## 关联本体节点
```
ontology:pattern/ontology-modular-reference
ontology:domain/skill-to-tickets
ontology:domain/ontology-deep-integration-overview
```

## 风险与对策
- 风险：相似度误报噪音。对策：阈值可配，仅提示前3，人工确认后才写边
