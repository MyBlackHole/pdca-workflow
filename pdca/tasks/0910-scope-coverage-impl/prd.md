# 覆盖门禁判定器实施

## 背景
T2112推荐A声明覆盖。用户拍板do→check硬门禁、triage产scope-declare.json。

## 验收标准

- [ ] AC-1: 判定器与测试已产出，缺声明失败覆盖通过
- [ ] AC-2: 声明管线文档已同步，triage产声明门禁只验包含
- [ ] AC-3: 收敛valid:true且证据已登记

## 关联本体节点

```
ontology:concept/scope-coverage-gate
ontology:concept/pdca-evidence
ontology:domain/skill-triage-work
```

## 拆分映射

- 判定器与测试 -> ontology:concept/scope-coverage-gate
- 声明管线文档 -> ontology:domain/skill-triage-work
