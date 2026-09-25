---
schema: pdca.asset/v2
id: ontology:concept/task-decomposition
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-25'
summary: DECOMP-01：正式工作节点按独立交付拆分，不按执行操作拆分
---

# DECOMP-01：正式工作节点按独立交付拆分，不按执行操作拆分

本页只定义**正式工作节点**的拆分。当前已批准 Do 内为了隔离上下文、并行或缩小执行范围的切片，
使用 [CONTRACT-01](pdca-execution-contract.md) 的 Do-only Work Unit，不创建新的 PDCA 任务。

正式候选孩子必须同时具备独立职责、固定输入/输出、可独立拒收的成果和验证边界。
创建文件、写方法、补测试、运行命令通常只是一个节点内部的 Work Unit 或步骤，
不因操作数量、代码行数、预计工时、模块数量或 Agent 置信度增加而自动创建 Agent。

给出独立拒收见证、共享接口、组合责任和实际上下文负担；没有实质独立交付就保持 leaf，
在 Do 内用 Work Unit 分解。不要以少 Agent、少 token 或提高并行度为理由
合并已固定的独立义务，也不要为“提高并行度”凭空拆出正式节点。

分解只产生候选 seed、依赖和理由，向用户展示；用户明确工作级创建操作后才由宿主创建。
每个正式节点由自己的 Agent 执行完整 Plan→Do→Check→Act，父 Agent 不监控其生命周期、
不替其推进阶段。新孩子、新 scene 或新 attempt 都不继承未来授权。
