# 审查design与review回写与生产机制

## 背景
承接T2072结论与用户追问：design/review在Do内无显式本体沉淀字样，观感缺回写与生产，需双轴审查判定是机制缺口还是有意分层。

## 验收标准

- [ ] AC-1: 双轴审查报告已产出，Standards/Spec各有判定
- [ ] AC-2: 回写缺口已定位至具体门禁代码与本体节点
- [ ] AC-3: 证据已登记，收敛valid:true

## 关联本体节点

```
ontology:process/flow-do
ontology:process/flow-act
ontology:concept/pdca-gate-do
ontology:domain/skill-code-review
```

## 拆分映射

- Standards轴审查 -> ontology:domain/skill-code-review
- Spec轴审查 -> ontology:process/flow-do
- 回写门禁核验 -> ontology:process/flow-act
