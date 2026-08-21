---
schema: pdca.asset/v1
id: T0218-0808-backup-server-architecture
phase: check
source_ids: [research-report, design, convergence-map, poc-report]
---

## 上下文

任务要求产出「全量备份生态架构调研报告」+「完整备份产品架构设计」，覆盖客户端、服务端、
存储、调度、恢复五大子系统，并衔接既有 RPC 项目能力（epoll 服务端、PAR/RANGE 并发传输）。

调研通过 4 个并行子代理（dispatching-parallel-agents）+ websearch/webfetch 执行，
覆盖 6 个子问题；交付物为 `workspace/research-report.md` 与 `workspace/design.md`。

用户在 Check 阶段追加要求"测试调研到的每个产品进行 POC"，并确认范围为**工具类
（排除 ZFS/LVM 文件系统类）**、全维度验证、合成+真实数据结合。据此对 5 个工具类
产品（rsync/Borg/Restic/Rclone/Duplicity）完成实测，产出 `poc/poc-report.md`。

## 假设与结果

- 假设：主流备份工具存在可提炼的通用架构模式（CDC 去重、快照/manifest、先压缩后加密、
  顺序写存储），服务端程序采用 epoll/Reactor 事件驱动模型。
- 结果：假设全部成立。
  - 报告覆盖 10 个备份工具/框架（rsync、Borg、Restic、Rclone、Duplicity、Bacula、Amanda、
    ZFS send、LVM 快照），每个含核心架构、关键设计决策、适用场景、引用来源。
  - 报告覆盖服务端架构模式 5 项（网络 IO 模型、事件循环/线程模型、并发与内存管理、
    存储/调度/高可用、对自研服务端的启示）。
  - 设计文档覆盖五大子系统，含组件图、数据流、关键决策清单（D1-D10 全部回溯到
    `[R:x.y]` 调研标注或既有 RPC 能力）。
  - **POC 实证**：Borg 增量去重 8.11M（98.3%）、Restic 461M→260M、双快照 PITR 成功、
    gpg 加密性能短板实测确认（10.2s vs Borg 2.97s）。
  - **性能基准**（用户要求补测，三档规模 × 耗时 × RSS）：rsync/rclone 最快且轻
    （1.1s/5MB）；Restic 多线程充分利用 16 核（user 31.5s vs wall 2.38s）但 RSS 高
    （396MB）；**Duplicity 增量退化至≈全量耗时**（461MB 档 5.69s vs 5.54s，librsync
    差分特性），验证 CDC 快照式选型正确。
  - **单文件基准**（用户再补充）：CDC 工具有固定启动开销（小文件 Borg/Restic
    ~0.5-1.1s vs rsync 0.06s），大文件吞吐 rsync 439MB/s > Duplicity 34MB/s →
    自研引擎需批量打包小文件 + 大文件独立大块路径。

## 分析

- **AC-1（≥8 工具）**：10 个工具，四要素齐全 ✅
- **AC-2（服务端架构模式）**：5 小节，每项含权威引用 ✅
- **AC-3（五大子系统）**：客户端/服务端/存储/调度/恢复各成章，含数据流与决策 ✅
- **AC-4（衔接 RPC 项目）**：第 8 章映射表 + D6/D9 决策明确引用 `rpc-epoll`、
  `rpc-protocol.h` PAR/RANGE、`--backup-inc`、`--meta-find-range` ✅
- **AC-5（引用真实性）**：34 个引用 URL 全量 curl 复测均返回 200（Amanda/Bacula/Netty/
  unixism/RedHat 等 5 处 404/403 均已替换为已验证的官方地址）✅
- **AC-6（独立完整文档）**：两份 Markdown 可单独阅读，结构完整 ✅
- **POC 回归**：调研结论经实测确认，无颠覆性修正。唯一修正点为"加密实现选型"
  （内置 AES 优于外部 gpg），已在 design.md 决策清单补充 POC 实证列。

## 失败原因

无（verdict 为 confirmed）。

## 适用边界

- 本任务为纯研究/设计 + 本地 POC 实证，无运行时代码；结论的可验证性在于引用可访问性、
  设计决策可回溯、POC 数据可复现（固定种子合成数据集）。
- POC 为本地单机磁盘场景，未测远程存储后端（网络受限）、多客户端并发、PB 级索引。
- 未测 Bacula/Amanda（无官方仓库包、AUR 不可达、依赖重、无 root）。
- 去重率、块大小等参数需在实现阶段通过更大规模基准校准。

## 下一轮建议

- 若继续推进：可创建实现任务，按 design.md 第 8 章「需新增」清单（CDC 分块器、块指纹
  查重、压缩/加密层、manifest 原子提交、后端存储抽象、refcount 回收）分模块落地。
- 实现前建议复用本 POC 的合成数据集与指标框架做实现级基准对照。
- 补充网络传输/多客户端场景 POC（环境允许时）。
