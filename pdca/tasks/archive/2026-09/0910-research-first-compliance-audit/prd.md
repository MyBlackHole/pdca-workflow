# 审查全场景先调研产本体满足度

## 背景
T2092先调研门禁与T0513回写强制均已上线，需复审六场景是否满足任务必须先调研产出本体的要求。

## 验收标准

- [ ] AC-1: 双轴审查报告已产出，Standards/Spec各有判定
- [ ] AC-2: 六场景满足度已逐项判定，缺口定位至门禁代码与本体节点
- [ ] AC-3: 证据已登记，收敛valid:true

## 关联本体节点

```
ontology:process/flow-do
ontology:process/flow-act
ontology:concept/research-first-gate
ontology:concept/pdca-ontology-ready
```

## 拆分映射

- Standards轴审查 -> ontology:domain/skill-code-review
- Spec轴审查 -> ontology:process/flow-do
- 回写核验 -> ontology:process/flow-act
