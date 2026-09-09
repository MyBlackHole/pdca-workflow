# research强制网络查询门禁实施

## 背景
T2073确认：research应强制网络查询，现仅推荐。需落为可回归门禁。

## 验收标准

- [ ] AC-1: 门禁脚本与测试已产出，缺URL判失败有URL通过
- [ ] AC-2: skill-research已更新强制条款并通过validate
- [ ] AC-3: 收敛valid:true且证据已登记

## 关联本体节点

```
ontology:domain/skill-research
ontology:domain/skill-web-research
ontology:concept/pdca-gate-do
```

## 拆分映射

- 校验脚本与测试 -> ontology:domain/skill-research
- 技能条款更新 -> ontology:domain/skill-web-research
- 门禁联调 -> ontology:concept/pdca-gate-do
