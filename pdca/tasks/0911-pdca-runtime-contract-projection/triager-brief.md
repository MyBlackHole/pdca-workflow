# Triage Brief - pdca-runtime-contract-projection

- **category**: enhancement
- **ontology_role**: `ontology_projection`; **execution_contract**: 在新 runtime 核心中投射职责/契约驱动的一对一子 Agent 派发、挂起、当前任务恢复和符合性验证，并迁移配置、Schema、入口与测试
- **summary**: 将已确认的 PDCA 子 Agent 执行不变量投射为可执行 runtime，彻底移除旧场景路由和主会话回退。
- **current behavior**: 核心本体已按三个专业职责建模，但机读 contract、能力配置、诊断和部分门禁仍消费旧场景或允许主会话回退，且没有持久化 Agent 执行状态机。
- **desired behavior**: 当前任务的专业职责和四字段执行契约是唯一行为输入；每轮 Do 绑定全新子 Agent，协调器派发后挂起，恢复只读取当前任务资料并执行符合性验证，spawn 缺失时 fail-closed。
- **key interfaces**: 严格任务合约、能力探针、Executor Adapter、派发请求与回执、当前任务执行状态、证据与收敛验证。
- **acceptance criteria**: 运行 runtime 目标测试得到三职责正向通过及缺失能力、旧角色、摘要漂移、重复派发、跨任务恢复和主会话回退负向拒绝；运行完整回归和本体检查得到可区分的通过报告。
- **out of scope**: 具体平台 Agent API、shell 启动 Codex、关联任务状态检查、历史身份修复、旧模型兼容层。
- **information gaps**: 无阻断性事实缺口；最终实现文件边界由子 Agent 在新核心目录内按测试驱动收敛。
- **dedup results**: T2175/T2178 是本体来源与清理前置；T2164/T2165 基于已废弃 A/B/C 模型，不能复用。未发现同目标的有效 runtime 投射任务。
- **recommended next steps**: 完成 Plan 终审后，由一个全新原生子 Agent 独立执行当前 PDCA；协调会话挂起，恢复后仅审查 T2181 持久化产物。
