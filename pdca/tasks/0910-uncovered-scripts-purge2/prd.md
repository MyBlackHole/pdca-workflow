# 无本体覆盖脚本第二轮purge

## 背景
T2127删除PDCA本体未覆盖逻辑脚本已归档（删25留10，结论冻结于当时点）。当前scripts/约50项，含T2127后新增脚本，覆盖状态未知。用户确认全量重审残留，沿用T2127判据，dry-run先行确认。

## 验收标准

- [ ] AC-1: dry-run分级清单已逐项确认去留（沿用T2127四类保留：运行时导入/kept调用/CI链/他人在途）
- [ ] AC-2: 删除后全绿已提交，可revert（pytest失败集与删前一致，validate通过）
- [ ] AC-3: 收敛valid:true且证据已登记（blast-report/deletion-manifest/convergence-map）

### 声明的测试接缝

- seam: tests/test_purge2_blast.py -> scripts/pdca_core.py
- seam: tests/test_purge2_blast.py -> scripts/transition-phase.py

## 关联本体节点

```
ontology:concept/meta-ontology
ontology:concept/process-complexity-ruling
ontology:concept/pdca-evidence
```

## 拆分映射

- 判据复核与全量扫描 -> ontology:concept/meta-ontology
- dry-run分级清单 -> ontology:concept/process-complexity-ruling
- 删除回归与证据登记 -> ontology:concept/pdca-evidence
