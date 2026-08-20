---
schema: pdca.asset/v1
id: T0300-0820-backupstream-arch-diagram
phase: check
source_ids: [arch-diagrams-full, research-report-v1, convergence-map-v2]
---

## 上下文

任务 T0300 对 backupstream 171.0.0 全项目源码（四二进制 + RSP/6 协议 + 运行时，176 源文件约 8.8 万行）进行函数级图文分析，产出 `docs/ARCH_DIAGRAMS.md`（纯 Mermaid、全中文、极致逐函数级、含对象生命周期图）。用户经 P2 Grill 明确：产出放项目 docs/ 新文档、覆盖全项目、60-80+ 图、纯 Mermaid、全中文+术语对照，并补充要求 5 类对象生命周期图。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 单一主文档 `docs/ARCH_DIAGRAMS.md` 承载全部图文 | 达成：十大章 1350+ 行，无跨文档漂移 |
| 60+ 张纯 Mermaid 图且语法全部可渲染 | 达成：60 张，mmdc 逐图渲染 0 失败 |
| 每张图含中文标签与 `图例：` 行 | 达成：60/60 图全部含中文标签，60 行图例 |
| 5 类生命周期对象各至少一张 stateDiagram | 达成：BackupResult/Manifest/会话/Data Lane/EXEC 子进程 5 类全覆盖 |
| 源码引用可 grep 核验 | 达成：47 个引用文件全部存在（修正 8 个不实路径） |
| Agent 零状态/双事实等核心不变量有源码+文档双重证据 | 达成：1.3/1.4 节引用 README/docs/ARCHITECTURE.md 原始表述 |

## 分析

- 架构结论：控制面（backupctl/backup-dirtyd/backup-observe）持有备份语义，执行面（backup-agent）零持久化状态；网络双路径（Plain 单 Reactor+11 态 ingress vs TLS Reactor Group+9 态分发）；六执行运行时 FSM 共享三层执行域；持久化按不可变 Manifest（v9 prepared→final 两阶段）/可变 Catalog（SQLite/LMDB）/dirty journal 分层。
- 过程问题与修正：8 个源码引用路径不实（如 `agent_restore_runtime.cpp` 实为 `agent_restore_reactor.cpp`、`dirty_journal.cpp` 实为 `client_dirty_journal.cpp`），已批量修正并经存在性复验；两张图 Mermaid 语法错误（subgraph 标题含 `,`/`()`、flowchart 边标签 `--> label` 误用）已修复并通过 mmdc 复验。
- 门禁通过：收敛校验 `valid: true`（convergence-map-v2），全部 14 条 AC 有非 map 证据覆盖。

## 失败原因

无（verdict 判定见 meta.verdict）。

## 适用边界

- 文档面向 171.0.0 源码快照，不承诺跟踪未来版本演进；未覆盖 OPENSSL 握手字节级细节；无性能断言。
- 图表规范经验（Mermaid 保留字符、文件名真实性核验）已可在后续图文任务复用。

## 下一轮建议

- 将 60 张图的渲染产物（SVG）纳入持续校验脚本（CI 前置门禁），防止文档回归。
- 为 `agent_restore_reactor`/`client_restore_runtime` 等命名易混模块补充 CONTEXT.md 术语条目。