# Triage Brief — 0820-backupstream-arch-diagram

- **category**: enhancement
- **scenario_type**: research
- **summary**: 分析 backupstream 171.0.0 全项目源码（四二进制 + RSP/6 协议 + 运行时），产出以纯 Mermaid 图表为核心、中文标注的非常详细的流程图与架构图文档，写入项目 `docs/`。
- **current behavior**: 项目 `docs/` 已有 ARCHITECTURE/PROTOCOL/RUNTIME/OPERATIONS/TESTING/DEVELOPMENT 等文字文档，但无面向当前 171.0.0 源码的、以图表为主的分层图文总览；此前 T0287 产出过 80.0.0 的 ARCH_IMPLEMENTATION.md（已不适用当前版本）。
- **desired behavior**: 一份（或分卷）docs/ 下新文档，覆盖：系统总览架构图、backupctl 客户端全链路、backup-agent 服务端（ingress/TLS/运行时）、backup-dirtyd 守护、backup-observe 诊断、RSP/6 协议帧流、Reactor 事件模型、工作池/调度器、数据通道/EXEC/恢复 等，极致逐函数级（预计 80+ 张 Mermaid 图），全中文正文 + 术语英文原名对照。
- **key interfaces**: 四二进制入口（backupctl/backup-agent/backup-dirtyd/backup-observe）；RSP/6 帧类型与能力位；reactor 事件循环与 reactor_group 分片；work_pool/cpu_scheduler/storage_backend 三层执行域；agent_plain_ingress 握手状态机；TLS 运行时与会话分发；TREE/FILE/RESTORE/DATA LANE/EXEC 各运行时 FSM；manifest v9 / catalog 持久化。
- **acceptance criteria**: 见 prd.md（逐条独立可验证，按源码引用可 grep 核验）。
- **out of scope**: 不修改任何 src/ 源码；不改既有 docs 文档；不做基准测试与性能断言；不逐文件穷举 ROUND 历史。
- **information gaps**: 无（源码函数级结构已由探索子代理完成分析）。
- **dedup results**: 相似历史任务 T0287（80.0.0 架构分析，research，已归档）、T0297（reactor 相位图形化，documentation，已归档）。当前 171.0.0 源码与 80.0.0 差异巨大（TLS 路径、EXEC 移交、manifest v9 等均为新增），且本任务以纯 Mermaid 图表为主、覆盖全二进制，不属于重复。out-of-scope 无命中。
- **recommended next steps**: 按 research 路径 C 执行；产出 docs/ 下新图文文档并在 PDCA record evidence 登记副本。