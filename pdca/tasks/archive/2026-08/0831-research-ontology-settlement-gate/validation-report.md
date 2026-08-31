# T0465 验证报告

## ontology-validate

```
OK: ontology 通过本体契约校验
exit:0
```

## ontology_graph

```
# Ontology graph summary
nodes: 350
edges: 759
islands: 0
exit:0
```

## check-research-ontology-settlement

### 正例 T0464
```
OK: research settlement decision present for T0464 (record=T0464-0831-prod-tool-dev-requirements-research, phase=archive)
```

### 负例拦截
```
RESEARCH_SETTLEMENT_MISSING: conclusion.md missing '## 本体沉淀' section
RESEARCH_SETTLEMENT_MISSING: meta.disposition.reason must contain 'ontology' or 'records-only'
exit:1
```

## SKILLS-INDEX
- `python3 scripts/generate-skills-index.py` 已执行，asset_count 48

