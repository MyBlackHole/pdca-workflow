# EvidenceAdapter 演示输出

执行：
```
python3 scripts/ontology_induction.py --adapter evidence --source records/T0454-0831-research-last-two-commits/evidence/manifest.jsonl --out print
```

输出 3 候选：
- ontology:concept/evidence-document-ev-report (guides: [])
- ontology:pitfall/evidence-pitfall-ev-pitfall (specializes pitfall, guides: [])
- ontology:concept/evidence-convergence-map-convergence (guides: ontology:entity/evidence-convergence-map)

说明 EvidenceAdapter 正确读取 manifest.jsonl 的 evidence_type_ref 并映射 guides。
