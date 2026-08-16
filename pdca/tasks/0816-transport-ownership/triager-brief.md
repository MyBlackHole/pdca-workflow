# Triage Brief — 0816-transport-ownership

- **category**: enhancement
- **scenario_type**: research
- **summary**: 分析 backupstream v101 的传输所有权设计：plain 与 TLS 双径如何各自拥有 socket/传输，两类传输如何通过统一 transport adapter 与共享业务 FSM 协作，所有权在 Reactor/Work Pool/共享事件域之间的转移边界。
- **current behavior**: Agent 侧存在两条传输路径——plain（单 Reactor + `agent_plain_ingress`，业务帧完全 Reactor 化）与 TLS（`reactor_group` 分片 + `tls_reactor_conn_t`）；两径均通过 transport adapter（emit_frame/resume_rx/tx_bytes/request_close）驱动共享的 TREE/FILE/RESTORE/Lane FSM；EXEC 在 plain 下二次转移到共享 EXEC 事件域，TLS 下留在 TLS Reactor。
- **desired behavior**: 产出一份系统化的「传输所有权设计」分析文档，覆盖：两径所有权归属模型、传输 adapter 抽象、所有权转移点（ingress→FSM→work pool→EXEC 域）、每个转移的并发安全契约、以及双径一致性与差异。
- **key interfaces**: reactor/reactor_group/tls_reactor_conn_t、agent_plain_ingress、transport adapter（emit_frame/resume_rx/tx_bytes/request_close）、agent_tree_reactor/agent_file_reactor/agent_restore_reactor/agent_lane_group、work_pool、EXEC 共享事件域、Data Lane 物理通道、client 侧运行时。
- **acceptance criteria**: 输出报告存在且覆盖：a) plain 与 TLS 各帧类型的 socket 所有权归属表；b) transport adapter 接口语义与两径实现对照；c) 至少 4 个所有权转移点（ingress→business FSM、FSM→work pool、plain EXEC→共享域、lane attach→lane FSM）的并发安全契约；d) 双径差异与设计理由；e) 所有权边界违反风险清单。
- **out of scope**: 不改码；不做性能优化方案（T0294 已覆盖）；不重新分析 git 演进（T0295 已覆盖）；不重新分析 Reactor 相位会计（T0296/T0297 已覆盖）。
- **information gaps**: TLS 侧所有权转移的具体点需源码核实（tls_reactor 的 connection_acquire/request_close 语义）；client 侧与 Agent 侧所有权模型的对应关系。
- **dedup results**: T0294 关注"如何提升"（优化方案设计），本任务关注"现状如何组织"（所有权设计分析），角度不同不重复；T0287 为 80.0 架构总览，T0295 为演进学习，本任务聚焦传输所有权单一维度深挖。
- **recommended next steps**: Plan 阶段源码深度核实 TLS 侧所有权转移点，产出 PRD 后经用户终审进入 Do。