# 证据：AC-4 删除 knowledge/ 并校验
- `git rm -r knowledge/` 执行成功，目录已不存在。
- `ontology-validate.py` → OK；`ontology_graph.py --format summary` → nodes:239 edges:489 islands:0。
- ontology-validate 对缺失 knowledge/ 有存在性保护（不阻断）。
