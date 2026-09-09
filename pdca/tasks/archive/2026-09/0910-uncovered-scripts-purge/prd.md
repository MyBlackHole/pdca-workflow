# 删除PDCA本体未覆盖逻辑脚本

## 背景
用户要求删除PDCA流程本体未覆盖的逻辑脚本。初筛35候选含误判与高危项，须逐项裁决后删。

## 验收标准

- [ ] AC-1: 覆盖判据已对齐并落盘grilling确认
- [ ] AC-2: dry-run清单已逐项确认去留
- [ ] AC-3: 删除后全绿已提交，可revert

## 关联本体节点

```
ontology:concept/meta-ontology
ontology:concept/process-complexity-ruling
ontology:domain/skill-research
```

## 拆分映射

- 判据与分级 -> ontology:concept/meta-ontology
- dry-run清单 -> ontology:concept/process-complexity-ruling
- 删除回归 -> ontology:domain/skill-research
