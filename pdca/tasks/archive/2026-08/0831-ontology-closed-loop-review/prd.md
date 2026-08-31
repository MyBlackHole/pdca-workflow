# 审查本体论完整闭环融入与 mattpocock/skills 可借鉴内容

## 背景

本项目已建立 PDCA 工作流本体（340 节点，703 边，0 孤岛），并已对照 mattpocock/skills v1.2.3 完成多轮差距识别（P0/P1/P2）。本任务在已有基础上，完成三项更深层审查：

1. 本体论是否完整融入于使用完成闭环
2. mattpocock/skills 是否还有可借鉴的内容没有学习到
3. 某个内容产生本体知识的机制，以及开发依赖本体知识进行任务拆分与单元测试的闭环

## 验收标准

- [ ] AC-1：完成本体论在 PDCA 全周期（plan→do→check→act→archive）闭环融入度的逐阶段审查
- [ ] AC-2：完成 mattpocock/skills 最新版本与本地本体的差距对照，识别新增可借鉴内容
- [ ] AC-3：完成本体知识产生→任务拆分→单元测试的依赖链调研，识别闭环缺口
- [ ] AC-4：输出带优先级（P0/P1/P2）的改进计划，每项关联本体节点或任务
- [ ] AC-5：所有结论经 `ontology-validate` 通过且 `ontology_graph` 无新增孤岛

## 收敛条件

- convergence-map 逐条回链 PRD AC 到 evidence ID
- 所有改进项有关联的本体节点或任务 ID
- 改进计划经用户 final_confirmation 确认

## 范围边界

- 本任务为 review 类型，不直接产出代码实现
- 改进计划的具体实施需创建对应子任务后执行
- 基于 mattpocock/skills 最新快照（含 v1.2.3 后变更）
