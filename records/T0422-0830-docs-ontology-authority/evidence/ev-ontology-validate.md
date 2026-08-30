# 证据：AC-8 本体校验通过
- `python3 scripts/ontology-validate.py` → OK，exit=0。
- `python3 scripts/ontology_graph.py --format summary` → nodes:89 edges:189 islands:0。
- 全仓（排除 records/journal/tasks）grep `docs/` 仅剩本体节点「原 docs/... 来源」历史注记，无指向已删 docs/ 文件的实时引用。
