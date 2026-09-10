# 判据复核与全量扫描

## 验收标准

- [ ] AC-1（回链父 AC-1）: T2127四类保留判据适用性已复核，结论落盘research-report
- [ ] AC-2（回链父 AC-1）: 当前scripts/全量约50项逐项四维扫描，引用证据可复核
- [ ] AC-3（回链父 AC-1）: T2127已删25项不重审，新增疑似项已识别

### 声明的测试接缝

- seam: tests/test_purge2_blast.py -> scripts/pdca_core.py

## 关联本体节点

```
ontology:concept/meta-ontology
ontology:concept/process-complexity-ruling
```

## 拆分映射

- 判据复核 -> ontology:concept/meta-ontology
- 全量扫描 -> ontology:concept/process-complexity-ruling
