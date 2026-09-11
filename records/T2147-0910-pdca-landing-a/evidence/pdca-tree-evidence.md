# PDCA 流程本体树证据（T2147）

## 判定

PDCA 流程本体满足本体树要求：以 `ontology:concept/pdca` 为根的引用子树
468 节点（全库 562），四 flow 一步直连，悬空边 0，无向孤岛 0，`specializes` 无环。

## 数据

- 根：`ontology:concept/pdca`（1.0.3）
- 子树节点清单：`pdca-subtree.json`（468 id，`pdca.tree-evidence/v1`）
- 四 flow 路径：`flow-plan/do/check/act → part_of → pdca`（长度 1）
- 全库：`ontology_graph --format summary` → nodes 562 / edges 1686 / islands 0
- 契约校验：`ontology-validate` OK（AC-1 类型受控 / AC-2 非空悬 / AC-3 无环）

## 复核途径

```bash
python3 scripts/ontology-validate.py 2>&1 | tail -n 1
python3 scripts/ontology_graph.py --format summary
python3 -c "import json; d=json.load(open('pdca/tasks/0910-pdca-landing-a/pdca-subtree.json')); print(d['node_count'], d['dangling_edges'])"
grep -n "part_of" ontology/process/flow-*.md
```
