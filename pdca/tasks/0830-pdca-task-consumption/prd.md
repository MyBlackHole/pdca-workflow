# T0417 消费 pdca-task 元概念驱动任务表达

- 任务 ID：T0417
- 依赖：T0416（本体关系树驱动任务拆分，已完成）
- 场景类型：development

## 背景与问题

审查确认 `ontology:concept/pdca-task` 元概念节点（定义"PDCA 任务元概念：由 task.json 跟踪 phase/status，阶段只经 transition 合法边推进，final_confirmation/check_confirmation 不可 AI 代签"）**未被任何流程/脚本消费来塑造任务表达**。T0415/T0416 让 `to-tickets`/`task_identity` 支持了 `ontology_node_type` 透传/继承与关系树推导，但创建任务时：
1. 没有任何地方把任务显式锚定到 `pdca-task` 元概念——任务是"孤儿"，未挂接本体图谱；
2. `ontology_node_type` 的合法类型词表来自 `ontology-asset.schema.json` 与脚本常量 `TYPE_VOCAB`（硬编码），未回到 `pdca-task`/本体作为唯一事实源；
3. 任务表达的不变量（不可 AI 代签等）未在创建时回链 pdca-task 元概念。

## Seam 分析

### 测试接缝
- `scripts/task_identity.py`：创建任务时锚定/校验 `pdca-task` 元概念、加载本体受控类型词表校验 `ontology_node_type`。

### 声明的测试接缝
- seam: tests/test_pdca_task_consumption.py -> scripts/task_identity.py

## 设计概览

### Part 1 任务锚定 pdca-task 元概念
- `task_identity.py` 创建任务时，默认写入 `meta.ontology_anchor = "ontology:concept/pdca-task"`（除非 `meta.ontology_exempt=true`）。
- 创建时校验该本体节点存在且 `type == "concept"`；缺失或类型不符时报错退出（保持顾问式：仅锚定不阻断其他字段）。
- 子任务自动继承父任务的 `ontology_anchor`（与 `ontology_fragment`/`ontology_node_type` 继承一致）。

### Part 2 受控类型词表来自本体（非硬编码）
- 新增 `ontology_reason.controlled_node_types()`：优先从本体 `ontology:concept/ontology-asset`（pdca-task 关联资产节点）读取声明的受控类型列表；节点/声明缺失时回退到脚本常量 `TYPE_VOCAB`。
- `task_identity.py` 校验 `--ontology-node-type` / `meta.ontology_node_type` 时改用此函数，使"类型词表唯一事实源"真正落到本体（呼应 README §9「节点是门禁参数唯一事实源」）。

### Part 3 Plan 阶段回链提示
- `flows/flow-plan/SKILL.md` P1 提示：任务即 `pdca-task` 元概念实例，其不变量（final_confirmation/check_confirmation 不可 AI 代签、phase 仅经 transition 合法边推进）由 `ontology:concept/pdca-task` 定义，任务表达应回链该节点。

### Part 4 测试
- `tests/test_pdca_task_consumption.py`：锚定默认写入/豁免跳过、锚定节点缺失报错、node_type 校验采用本体词表、非法 node_type 拒绝、子任务继承锚定。

## 验收标准

- [ ] AC-1（锚定）：`task_identity.py` 创建任务默认写 `meta.ontology_anchor=ontology:concept/pdca-task`（除非 exempt），并校验该节点存在且 type=concept；子任务继承父锚定。
- [ ] AC-2（词表本体化）：`ontology_node_type` 校验优先从本体 `ontology:concept/ontology-asset` 加载受控类型词表，缺失回退常量；非法 type 报错。
- [ ] AC-3（Plan 回链）：`flow-plan` P1 提示任务表达回链 `pdca-task` 元概念不变量。
- [ ] AC-4（测试）：新增测试覆盖锚定默认/豁免、词表加载、非法 node_type 拒绝、继承。

## 非目标

- 不改 `pdca-task` 元概念节点定义本身（仅消费）。
- 不强制所有任务声明 `ontology_node_type`（保持顾问式）。

## 风险与缓解

- 锚定节点缺失导致创建失败：仅当 `ontology_fragment=ontology`（或显式锚定）且节点缺失时报错；exempt 任务跳过，默认行为不受影响。
- 词表回退：本体未声明时回退常量，行为等价于现状，无回归。

## 关联本体节点

ontology:concept/pdca-task
ontology:concept/ontology-asset
