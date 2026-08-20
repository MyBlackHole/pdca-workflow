# 调研报告 — backupstream 171.0.0 全貌图文分析

## 调研目标

分析 backupstream 171.0.0 全项目源码（四二进制 + RSP/6 协议 + 运行时），绘制非常详细的流程图与架构图，产出 `docs/ARCH_DIAGRAMS.md`（纯 Mermaid、全中文、极致逐函数级，含对象生命周期图与资源元抽象关系）。

## 方法

- 五个探索子代理对 176 个源文件做函数级结构分析（客户端 22 文件、Agent 服务端、Agent 运行时/TLS、底层基础、持久化/工具）。
- 追加两个专项探索：lane↔socket 资源映射、海量小文件并发机制。
- 交叉核验关键枚举与函数：ingress 11 态（`src/agent_plain_ingress.cpp:34`）、TLS 9 态（`src/agent_tls_runtime.cpp:27`）、lane 10 态（`src/agent_data_lane.cpp:15`）、lane 组 8 态（`src/agent_lane_group.cpp:27`）、EXEC 3 态（`src/agent_exec_runtime.cpp:348`）、WireFrameHeader 16 字节（`src/protocol.hpp:203`）、manifest v9 发布（`src/backup_manifest.cpp:525-587`）、catalog compare（`src/backup_catalog.cpp:982`）。
- 64 张 Mermaid 图逐一经 mmdc 语法渲染校验（0 失败，SVG 产物全量生成），每张图含中文 `图例：` 行。
- 全部 56 个源码引用文件经存在性核验（缺失的 8 个文件路径已修正为真实文件名）。
- 渲染兼容性加固：所有 subgraph ID 由中文改为 ASCII + 中文 label，消除 GitHub/VS Code 旧版 Mermaid 渲染失败风险。

## 发现

1. **架构分层**：控制面（backupctl/backup-dirtyd/backup-observe）持有备份语义；执行面（backup-agent）零持久化状态。
2. **网络双路径**：Plain 走单 Reactor + 11 态 ingress FSM；TLS 走 Reactor Group 分片 + 9 态 TLS FSM + 三层执行域。
3. **协议 RSP/6**：16 字节帧头、68 种帧类型分 8 组、HMAC-SHA256 挑战应答认证、40 位能力位协商。
4. **资源元抽象（新增）**：每条 lane = 独立 TCP/TLS 连接（`lane_count+1 ≤ max_sessions` 校验、`reactor_lane_t` 独立 transport+connector、`lane_group_t.lane_fds[]` 跨连接汇聚）；channel 在 lane 连接上恒为 1，channel 0 保留控制；会话→通道→lane→socket 四层资源链；并发分用三层面（连接级/网络 epoll 分片/IO-CPU 分片）。
5. **海量小文件并发（新增）**：客户端单线程生产者 + FF_PIPELINED 流水线帧；小文件三级聚合（≤512KB 判定 → ≤1024 文件/包 → agent 8 文件/256KB task）；TREE_BARRIER 累积栅栏；inflight 128/64 滞回水位；SmallLocalWriterPool 接收端并行；目录遍历为 BFS。
6. **执行运行时**：TREE/FILE/RESTORE/DATA LANE/EXEC 六运行时各自 FSM 驱动。
7. **持久化**：不可变 Manifest v9（prepared→final 两阶段发布）、可变 Catalog（SQLite/LMDB 双后端）、dirty journal（inotify generation 轮换）。
8. **事件模型**：reactor 用 token/generation 防失效、双优先级 post 队列、共享 timerfd 最小堆、dispatch 兴趣合并。

## 结论与建议

- 产出物 `docs/ARCH_DIAGRAMS.md`（64 张图、17 条 AC 全通过）完整覆盖用户要求的详细程度，含 5 类对象生命周期图、lane↔socket 资源映射、海量小文件并发机制。
- 建议后续复用本文档附录 A 源码索引作为新贡献者入门地图。
- 注意事项：Mermaid 节点标签中避免裸 `:`/`,`/`( )` 等保留字符；subgraph ID 必须用 ASCII；`agent_restore_runtime` 实为 `agent_restore_reactor`。

## 参考资料

- 项目源码 `src/`（171.0.0）、`docs/PROTOCOL.md`、`docs/ARCHITECTURE.md`、`docs/RUNTIME.md`、`README.md`
- 知识库 `knowledge/linux-epoll-eventloop/backupstream-plain-tls-ingress.md`、`backupstream-v65-v101-arch-evolution.md`
- 产出物 `docs/ARCH_DIAGRAMS.md`（本任务 evidence）