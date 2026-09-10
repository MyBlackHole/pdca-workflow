# dry-run分级清单

## 验收标准

- [ ] AC-1（回链父 AC-1）: dry-run清单逐项有去留结论与引用证据
- [ ] AC-2（回链父 AC-1）: 候选删除项经用户逐项确认
- [ ] AC-3（回链父 AC-3）: 悬空引用观察项已单列不混入删除

### 声明的测试接缝

- seam: tests/test_purge2_blast.py -> scripts/transition-phase.py

## 关联本体节点

```
ontology:concept/process-complexity-ruling
ontology:concept/pdca-evidence
```

## 拆分映射

- 分级清单 -> ontology:concept/process-complexity-ruling
