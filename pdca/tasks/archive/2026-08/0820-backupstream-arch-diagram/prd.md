# backupstream 171.0.0 全貌图文分析 — 规格文档

任务 ID: T0300
场景类型: research
来源: 用户需求「分析项目，绘制流程图、架构图，要求非常详细的程度」
创建: 2026-08-20

## 问题陈述

- **现状**: backupstream 171.0.0 源码约 176 个源文件（约 8.8 万行 C++），含四个二进制（backupctl / backup-agent / backup-dirtyd / backup-observe）。项目 `docs/` 已有 `ARCHITECTURE.md`（所有权模型）、`PROTOCOL.md`（RSP/6）、`RUNTIME.md`（Reactor/worker/I/O）、`OPERATIONS.md`、`TESTING.md`、`DEVELOPMENT.md`，但全部以文字为主、图极少，且无一份面向当前 171.0.0 源码、以图表为核心的分层图文总览。此前归档任务 T0287 产出的 80.0.0 架构报告已不适用于当前版本（TLS 路径、EXEC 移交、manifest v9、plain ingress 等均有重大演进）。
- **目标**: 产出 docs/ 下新图文文档，以纯 Mermaid 图表为核心、中文为正文、源码函数级引用为证据，系统性地绘制项目整体架构图与关键流程时序图，达到「极致逐函数级」详细程度。
- **差距**: 现有文档无法快速回答「四个二进制如何协同、RSP/6 帧如何流转、Reactor 事件域与工作池如何衔接、每个运行时 FSM 的完整状态转移、manifest/catalog 如何持久化」等结构化问题。

## 解决方案

新建 `docs/ARCH_DIAGRAMS.md`，以「分层递进 + 极致逐函数级」为原则组织。文档结构（十大章）：

1. **系统总览**：四二进制部署拓扑图、进程/线程拓扑、关键边界（Agent 零状态、BackupResult 双事实）。
2. **RSP/6 协议层**：WireFrameHeader 16 字节帧格式、68 种帧类型分组图、HELLO/认证握手时序、能力位协商、各操作族帧流（TREE/FILE/RESTORE/EXEC/DATA LANE）。
3. **客户端 backupctl**：命令分发树、会话握手时序、put 主流程（13 阶段）、目录处理流水线、manifest 两阶段发布时序、restore/verify 时序、data-lane 客户端状态机、TLS reactor（tree/exec/control）接线。
4. **Agent 服务端网络层**：acceptor 接受流程、plain ingress 11 态握手状态机、OPEN 分派中枢、控制作业多轮模型、READDIR 游标、TLS 栈装配、TLS 会话分发（8 态）、TLS 控制通道。
5. **Agent 执行运行时**：TREE 运行时 PUT/GET FSM、FILE 运行时 FSM、RESTORE reactor FSM、DATA LANE 单 lane FSM（9 态）、lane 组协调 FSM（7 态）、lane 注册表、EXEC TLS/plain 双模式 FSM、EXEC IO 泵事件域。
6. **事件与执行域**：reactor 事件循环（token/generation 防失效、双优先级 post、interest 合并、共享 timerfd）、reactor_group 分片选择、event_waiter 双后端、work_pool 公平调度、storage_backend 三层压力分派、cpu_scheduler 两级准入、bounded_admission、adaptive_window、regular_file_io 轮次。
7. **观测与审计**：observability exporter 线程模型、采样判定、审计链、server_status/storage_guard/systemd。
8. **backup-dirtyd**：inotify watch 生命周期、事件分类决策、rebuild 流程、dirty journal 准备/提交时序。
9. **backup-observe**：五子命令、迷你 JSON 解析、diagnose 时序分析阶段。
10. **持久化与数据流**：manifest v9 导出/校验/发布流程、catalog schema 与 compare 决策、dirty journal schema、restore state、hardlink tracker。

**对象生命周期图**（用户补充要求）：除架构图与流程时序图外，各章对关键业务对象补画生命周期图（stateDiagram-v2），包括但不限于：
- 系统总览章：BackupResult 双事实（payload + manifest）从产生到验证的完整生命周期；
- 客户端章：manifest 生命周期（prepared 候选 → 发布 → 崩溃回放三种分支）；
- Agent 网络章：会话生命周期（acceptor → 握手 → OPEN → 操作 → 关闭/超时/排空）；
- Agent 运行时章：Data Lane 单 lane 生命周期、lane 组生命周期、EXEC 子进程生命周期（spawn → 流 → 退出/超时 → reap）；
- 持久化章：catalog run 生命周期、dirty journal generation 生命周期、restore state 生命周期。

每张图遵循 code-comments 技能图示规范：Mermaid（flowchart/sequenceDiagram/stateDiagram-v2）为主、一张图一个意图、中文节点标签、必须带 `图例：` 行、≤20 行优先（复杂流程拆分）。每个关键函数在对应章节以源码引用（`src/file.cpp`）标注。

## Seam 分析

### 声明的测试接缝

research 场景无测试产物，跳过。

### 验收可测性

- 图表数量可用 `grep -c '```mermaid'` 核验；
- 源码引用可用 grep 复核存在性；
- 章节覆盖用标题 grep 核验。

## 用户故事

1. 作为新接手者，我想要一张能直接讲清「backupctl 如何把目录树备份到 backup-agent」的端到端时序图，以便快速建立心智模型。
2. 作为维护者，我想要各运行时 FSM 的完整状态转移图（TREE/EXEC/DATA LANE/ingress），以便定位热路径与状态机边界。
3. 作为架构读者，我想要四二进制部署拓扑与进程/线程分布图，以便理解资源边界与故障域。
4. 作为调试者，我想要 Reactor 事件循环与工作池衔接图（post/completion/interest 合并），以便理解异步路径。

## 实现决策

- 产出单一主文档 `docs/ARCH_DIAGRAMS.md`（内容量大时分章撰写但合并提交，避免多文档维护漂移）；项目既有文档不改动。
- 图表以纯 Mermaid 为主；正文全中文，术语首次出现含英文原名（如 Reactor、Work Pool、Data Lane、Manifest）。
- 以 171.0.0 源码为唯一事实来源，每个关键模块/函数附 `src/*.cpp` 引用，保证可 grep 核验。
- 参考既有知识 `knowledge/linux-epoll-eventloop/backupstream-plain-tls-ingress.md` 与 `backupstream-v65-v101-arch-evolution.md`，但版本事实以当前源码为准。
- 同一文档副本登记到 PDCA 记录 `records/T0300-0820-backupstream-arch-diagram/evidence/`。

## 测试决策

- research 场景，不做代码测试。
- 质量校验手段：`grep -c '```mermaid' docs/ARCH_DIAGRAMS.md` 计数图表；抽样 grep 源码引用验证存在性；标题 grep 验证章节覆盖。

## 验收标准

- [ ] AC-1: 文档写入 `docs/ARCH_DIAGRAMS.md`，含十大章节标题（系统总览/协议/客户端/Agent网络/Agent运行时/事件与执行域/观测审计/dirtyd/observe/持久化）
- [ ] AC-2: 文档中 Mermaid 图数量 ≥ 60 张（`grep -c '```mermaid'` 可核验），且每张图含中文节点标签
- [ ] AC-3: 每张 Mermaid 图均含中文 `图例：` 说明行（抽样 grep 可核验）
- [ ] AC-4: 系统总览章含四二进制部署拓扑图与进程/线程分布图
- [ ] AC-5: 协议章含 WireFrameHeader 帧格式图、HELLO 认证时序、能力位协商，各含源码引用
- [ ] AC-6: 客户端章含 put 主流程时序图（OPEN_PUT_TREE→目录队列→TREE_END→RESULT→manifest 发布）与 manifest 两阶段发布时序
- [ ] AC-7: Agent 网络章含 plain ingress 11 态状态机图（WAIT_HELLO→认证→WAIT_OPEN→分派）与 TLS 会话分发图
- [ ] AC-8: Agent 运行时章含 TREE PUT/GET FSM、DATA LANE 单 lane FSM、EXEC 双模式 FSM 三张状态机图
- [ ] AC-9: 事件与执行域章含 reactor 事件循环图（token/generation、双优先级 post、interest 合并）与 work_pool/storage_backend/cpu_scheduler 调度链图
- [ ] AC-10: dirtyd 章含 inotify watch 生命周期与 rebuild 流程时序图；observe 章含 diagnose 时序分析流程图
- [ ] AC-11: 持久化章含 manifest v9 导出发布流程与 catalog compare 决策流程图
- [ ] AC-12: 生命周期图覆盖：BackupResult、manifest、会话、Data Lane、EXEC 子进程 5 类对象各至少一张（stateDiagram-v2，含状态转移与触发条件）
- [ ] AC-13: 文档副本登记到 PDCA record `records/T0300-0820-backupstream-arch-diagram/evidence/`
- [ ] AC-14: 文档正文为中文，术语首次出现含英文原名；不修改任何 `src/` 源码与既有 `docs/` 文档
- [ ] AC-15: 资源元抽象关系图：含 lane↔socket 独立连接映射（N+1 条 TCP/TLS）、会话→通道→lane→socket 资源层级链、lane 三层并发分用模型（各至少一张图）
- [ ] AC-16: 海量小文件并发处理章节：含客户端单线程生产者+流水线帧、小文件三级聚合（512KB 判定/1024 文件包/8 文件 task）、TREE_BARRIER 累积栅栏、inflight 128/64 水位、SmallLocalWriterPool 接收并发
- [ ] AC-17: 渲染兼容性：所有 subgraph ID 使用 ASCII（不含中文），全部图在 Mermaid 9.4.3 / 10.9.1 / 11.16.0 三版本下渲染成功且 SVG 产物生成（mermaid-cli 逐图验证）
- [ ] AC-18: 典型场景案例章：7 个分章节小案例（全量备份/单大文件 lane 均分/lane 失败中止/增量比对/EXEC/崩溃恢复/dirtyd 守护+大文件恢复），每个案例含具体数字走查与对应章节回链
- [ ] AC-19: 对象生命周期图扩展：在 AC-12 基础上新增工作池任务、文件对象、TLS 会话、目录对象 4 类对象生命周期图（5.12-5.15，stateDiagram-v2 含状态转移与触发事件）
- [ ] AC-20: 对象关系图：5 张关系图（5.16 全局对象关系总图 / 5.17 客户端对象关系 / 5.18 Agent 对象关系 / 5.19 生命周期对象归属关系 / 5.20 客户端与服务端跨端对象关系），对象名与源码结构体一一对应，每条关系带源码证据

## 范围外

- 不修改任何 `src/` 源码、Makefile、CMakeLists。
- 不修改既有 `docs/*.md` 文档内容。
- 不做基准测试、不做性能断言。
- 不逐文件穷举历史 ROUND 报告。
- 不深入 OpenSSL 握手协议字节级细节（仅画应用层 TLS 会话流程）。

## 备注

- 源码函数级结构已由五个探索子代理完成前置分析（客户端 22 文件、Agent 服务端、Agent 运行时/TLS、底层基础、持久化/工具），本任务 Do 阶段直接复用该分析结果绘制图表。
- 图表规范参考 skill code-comments（已加载）：一张图一个意图、中文标签、带图例、Mermaid 语法自查。