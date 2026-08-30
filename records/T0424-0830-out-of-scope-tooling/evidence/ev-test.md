# 证据：AC-5 测试 + 校验
- `python3 -m pytest tests/test_out_of_scope.py -q` → 7 passed。
- `ontology-validate.py` → OK；`ontology_graph.py --format summary` → islands:0。
