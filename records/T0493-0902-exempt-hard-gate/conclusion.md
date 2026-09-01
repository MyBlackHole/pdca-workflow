# T0493 结论：豁免硬指标化

## 假设验证

成立。schema/gate/core三硬已落地，7历史exempt补理由，全绿。

## 结果

- AC-1 schema hard：exempt需reason≥20，doctor报 ONTOLOGY_EXEMPT_REASON_MISSING
- AC-2 gate hard：短理由/缺ontology被 ONTOLOGY_EXEMPT_REASON_MISSING 拒
- AC-3 core hard：records-only短理由被 DISPOSITION_RECORDS_ONLY_REASON_SHORT
- AC-4 历史7 exempt已补且 doctor清零
- AC-5 全绿 islands:0 ci GATE OK
- AC-6 收敛 valid:true

## 本体沉淀

硬指标已硬化，来源 T0493

## 证据索引

- ev-schema-v2/ev-gate/ev-core/ev-history/ev-convergence-map-v4

**verdict**: confirmed
