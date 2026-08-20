---
schema: pdca.asset/v1
id: T0300-0820-backupstream-arch-diagram
phase: check
source_ids: [arch-diagrams-v5, research-report-v2, convergence-map-v6]
---

## 上下文

任务 T0300 对 backupstream 171.0.0 全项目源码（四二进制 + RSP/6 协议 + 运行时，176 源文件约 8.8 万行）进行函数级图文分析，产出 `docs/ARCH_DIAGRAMS.md`（纯 Mermaid、全中文、极致逐函数级、含对象生命周期图与资源元抽象关系）。用户经 P2 Grill 明确：产出放项目 docs/ 新文档、覆盖全项目、60-80+ 图、纯 Mermaid、全中文+术语对照，并补充要求 5 类对象生命周期图。Check 后用户审查提出修正意见（渲染兼容性、资源关系、海量并发、可读性），已全面修正。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 单一主文档 `docs/ARCH_DIAGRAMS.md` 承载全部图文 | 达成：十大章 1538 行，无跨文档漂移 |
| 60+ 张纯 Mermaid 图且语法全部可渲染 | 达成：64 张，mmdc 逐图渲染 0 失败、SVG 全量生成 |
| 每张图含中文标签与 `图例：` 行 | 达成：64/64 图全部含中文标签，64 行图例 |
| 5 类生命周期对象各至少一张 stateDiagram | 达成：BackupResult/Manifest/会话/Data Lane/EXEC 子进程 5 类全覆盖 |
| 源码引用可 grep 核验 | 达成：56 个引用文件全部存在（修正 8 个不实路径） |
| 资源元抽象关系（lane↔socket）有真实源码证据 | 达成：5.9/5.10/5.11 三节，每条 lane 独立连接、资源层级链、三层分用均验证（`lane_count+1≤max_sessions`、`reactor_lane_t`、`lane_group_t.lane_fds[]`） |
| 海量小文件并发机制有真实源码证据 | 达成：3.12 节 + 表格，三级聚合/流水线/栅栏/水位/写池均验证（kSmallBlobTarget、kTreePutSmallBatchFiles=8、inflight 128/64、kDirectoryClaimBatch=64） |
| 渲染兼容性（GitHub/VS Code 旧版 Mermaid） | 达成：全部 subgraph ID ASCII 化 + 中文 label，移除 style 引用中文 ID |

## 分析

- 架构结论：控制面持有备份语义，执行面零持久化状态；网络双路径（Plain 单 Reactor+11 态 ingress vs TLS Reactor Group+9 态分发）；六执行运行时 FSM 共享三层执行域；持久化按不可变 Manifest（v9 prepared→final 两阶段）/可变 Catalog（SQLite/LMDB）/dirty journal 分层。
- 资源元抽象（修正新增）：每条 lane 独立 TCP/TLS 连接，lane_group 由第 N+1 条控制连接协调；channel 在 lane 连接恒为 1；会话→通道→lane→socket 四层资源链；并发分用三层面。
- 海量并发（修正新增）：客户端单线程生产者 + FF_PIPELINED 流水线；小文件三级聚合；TREE_BARRIER 累积栅栏；inflight 128/64 滞回。
- 过程问题与修正：8 个源码引用路径不实（如 `agent_restore_runtime.cpp` 实为 `agent_restore_reactor.cpp`）已修正；两张图 Mermaid 语法错误已修复；中文 subgraph ID 渲染兼容风险已全面 ASCII 化（20 处）。
- 门禁通过：收敛校验 `valid: true`（convergence-map-v4），全部 17 条 AC 有非 map 证据覆盖。

## 失败原因

无（verdict 判定见 meta.verdict；修正后用户复审确认）。

## 适用边界

- 文档面向 171.0.0 源码快照，不承诺跟踪未来版本演进；未覆盖 OPENSSL 握手字节级细节；无性能断言。
- 图表规范经验（Mermaid 保留字符、ASCII subgraph ID、文件名真实性核验）已可在后续图文任务复用。

## 下一轮建议

- 将 64 张图的渲染产物（SVG）纳入持续校验脚本（CI 前置门禁），防止文档回归。
- 为 `agent_restore_reactor`/`client_restore_runtime` 等命名易混模块补充 CONTEXT.md 术语条目。
- 可选：后续按需把 lane/socket 并发细节、小文件三级聚合拆成独立技术专题文档。