# AC-1 证据：任务创建本体感知（task_identity.py）

## 改动
- `scripts/task_identity.py`
  - 新增常量 `ONTOLOGY_NODE_TYPES`（与 ontology-validate.TYPE_VOCAB 对齐）。
  - `create_task` / `_create_task_unlocked` 新增参数 `ontology_fragment`、`ontology_node_type`，合并进 `meta`。
  - 新增 `_find_task_by_id` / `_inherit_ontology_meta`：子任务自动继承父任务 `ontology_fragment`/`ontology_node_type`，使拆分沿本体边界对齐。
  - 新增 `_validate_ontology_fragment`：片段须指向仓库内存在的本体目录，否则报 `ONTOLOGY_FRAGMENT_MISSING`/`NOT_DIR`；`ontology_node_type` 非法报 `ONTOLOGY_NODE_TYPE_INVALID`。
  - `_build_create` 解析 `--ontology-fragment`、`--ontology-node-type` 并透传。
- `schemas/task.schema.json`：meta 新增可选 `ontology_node_type`（枚举，约束在 TYPE_VOCAB）。

## 验证
- 新增 6 个单测（node_type 写入 / 非法拒绝 / 片段缺失拒绝 / 片段合法接受 / 父继承 / 默认 PRD 含关联小节），全部通过。详见 `ev-tests.log`（AC-1/AC-2 段）。
