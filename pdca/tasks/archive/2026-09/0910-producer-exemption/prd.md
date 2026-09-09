# research生产者豁免升级

## 背景
T2092/T2096锁定research自指阻断待升级。用户拍板生产者豁免。

## 验收标准

- [ ] AC-1: 生产者豁免已对齐并落盘grilling确认
- [ ] AC-2: 门禁测试已更新全绿，research叶放行非research仍阻断
- [ ] AC-3: 收敛valid:true且证据已登记

## 关联本体节点

```
ontology:concept/research-first-gate
ontology:concept/pdca-gate-do
ontology:domain/skill-research
```

## 拆分映射

- 豁免实现与测试 -> ontology:concept/research-first-gate
- 文档与本体同步 -> ontology:domain/skill-research
