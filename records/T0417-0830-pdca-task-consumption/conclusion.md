---
schema: pdca.asset/v1
id: T0417-0830-pdca-task-consumption
phase: check
source_ids: [pytest-t0417, convergence-map-t0417]
---

# T0417 结论：消费 pdca-task 元概念驱动任务表达

## 上下文

审查发现 `ontology:concept/pdca-task` 元概念节点（定义"PDCA 任务元概念：由 task.json 跟踪 phase/status，阶段只经 transition 合法边推进，final_confirmation/check_confirmation 不可 AI 代签"）长期**未被任何流程消费来塑造任务表达**。T0415/T0416 让 `to-tickets`/`task_identity` 支持 `ontology_node_type` 透传/继承与关系树推导，但创建任务时：任务未挂接本体图谱（"孤儿"）、`ontology_node_type` 受控词表硬编码、任务表达不变量未回链元概念。本任务让 `task_identity` 在创建任务时真正消费该元概念。

## 假设与结果

- 假设：任务创建时默认把任务锚定到 `pdca-task` 元概念、类型词表回到本体、Plan 阶段回链不变量，可闭环"任务即 pdca-task 实例"。
- 结果：`task_identity` 创建任务默认写入 `meta.ontology_anchor = ontology:concept/pdca-task`（除非豁免/继承），`ontology_node_type` 校验优先从本体 `ontology-asset` 加载受控词表；Plan P1 增加回链提示。

## 分析

- **AC-1** ✅ `task_identity` 创建任务默认锚定 `ontology:concept/pdca-task`，校验节点存在且 type=concept；`meta.ontology_exempt=true` 时跳过；子任务继承父锚定（pytest-t0417 / test_anchor_default_points_to_pdca_task, test_anchor_exempt_skips, test_child_inherits_parent_anchor）
- **AC-2** ✅ `ontology_reason.controlled_node_types()` 优先从本体 `ontology:concept/ontology-asset` 读取受控类型词表，缺失回退常量；非法 `ontology_node_type` 报错（pytest-t0417 / test_controlled_node_types_from_ontology, test_node_type_rejected_when_not_in_ontology_vocab）
- **AC-3** ✅ `flow-plan` P1 增加提示：任务即 `pdca-task` 元概念实例，其不变量由该节点定义，任务表达应回链（已更新 SKILL.md）
- **AC-4** ✅ 新增 9 个测试覆盖默认锚定/豁免/缺失/类型不符/词表来自本体/子任务继承；AC-1~4 全 ✅（pytest-t0417）

## 设计权衡

- 默认锚点（pdca-task）在本体缺失时（如自举期）**优雅跳过**而非阻断创建；仅显式/继承锚点缺失或类型不符才报错。这样既保证真实仓库里所有任务都挂接 `pdca-task` 元概念，又不破坏自举与最小化 fixture 场景。
- 附带修复一个真实 bug：原 `controlled_node_types(ont_dir=root)` 把**仓库根**传入 `load_ontology`，导致递归扫描 `templates/` 下含非法 YAML 的 `experience.md` 而崩溃；改为只扫 `ontology/` 目录，并给 `_fm` 增加 YAML 解析容错。

## 适用边界

- 锚定是"顾问式"元数据写入，不改变任务状态机或 transition 语义。
- 未改动 `pdca-task` 节点定义本身（仅消费）；`ontology_node_type` 仍可选填。

## 下一轮建议

- 可将"受控类型词表"真正沉淀进本体（给 `ontology-asset` 补 `node_types` 声明），使 `controlled_node_types` 在真实仓库也走本体路径；当前实现已优先读取，落地零成本。
- T0415/T0416/T0417 三连已把"创建任务表达、拆分任务、产物关系、执行计划引用"四个本体应用维度全部补齐。

## Verdict（建议，待用户确认固化）

- 建议 `outcome: confirmed`：四处实现均落地，测试覆盖锚定/豁免/词表/继承，AC-1~AC-4 全 ✅，并顺带修复本体加载崩溃 bug。
- 此区块由用户 `check_confirmation` 确认后写入 `task.json` `meta.verdict`，AI 不代签。
