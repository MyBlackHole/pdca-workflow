# backupstream 80.0.0 实现架构分析

> 本报告面向 **80.0.0** 源码实现，聚焦网络架构、线程架构、事件架构三大维度及其交互。
> 分析以源码为唯一事实来源；既有演进文档仅作背景参考，差异见「既有文档滞后差异清单」章节。

## 1. 总体架构

backupstream 是 Linux 远端文件/目录树备份运行时，采用 **client-owned 权威元数据目录（catalog）+ 服务端 root 约束对象存储** 的单一备份模型。

```text
┌──────────────────────┐        RSP/3 (TCP 或 TLS)       ┌──────────────────────┐
│      backupctl       │  ──────────────────────────────► │     backup-agent     │
│      (客户端)         │                                 │      (服务端)         │
│                      │                                 │                      │
│  · 权威 catalog       │                                 │  · root 约束对象        │
│    (SQLite/LMDB)     │                                 │  · 已提交 generation    │
│  · 持久化 backup-state│                                 │  · 大文件 partial+offset│
│  · 目录队列+游标       │                                 │  · System RPC (rootfd) │
│  · hardlink 追踪       │                                 │                      │
└──────────────────────┘                                 └──────────────────────┘
         │
         │ inotify 事件 (独立进程)
         ▼
┌──────────────────────┐
│    backup-dirtyd     │  可选首方脏日志生产者（独立长驻进程）
│  · wd→相对目录映射     │  使 inotify 观察不绑定于某一次 backupctl 生命周期
│  · file_index / dirty │
└──────────────────────┘
```

**进程边界**：

- `backupctl`：客户端 CLI，负责遍历、目录队列、catalog 提交、恢复编排。
- `backup-agent`：服务端，接受连接、执行 TREE/FILE/System RPC/EXEC，root 约束。
- `backup-dirtyd`：独立的脏目录观察进程，基于 `inotify`（`src/backup_dirtyd.cpp`），产出按代（generation）切分的脏日志，供 backupctl 选择性扫描。

**协议**：RSP 版本 3（`kProtocolVersion`，`src/agent_plain_ingress.cpp:52` 校验），v1/v2 帧直接拒绝，不迁移旧持久化 schema。

**连接状态模型**（`docs/DATA_LANES.md`）：逻辑 RSP 通道共享单一 TCP/TLS 传输；大文件可选独立物理 **Data Lane**（TCP/TLS）并行传输。

## 2. 网络架构

网络路径分 **两条主线**：非 TLS（plain）路径与 TLS 路径。这是本项目网络架构最核心的划分。

### 2.1 非 TLS（plain）路径：ingress 反应器 + 弹性会话池 + EXEC 事件域

v80 的关键演进是：**业务前握手阶段不再消耗阻塞工作线程**。

```text
listen fd (backup-agent)
   │  agent_acceptor_listener_cb (src/agent_acceptor.cpp:29) — accept burst ≤ 64，EMFILE 退避 100ms 定时器
   ▼
agent_plain_ingress_submit_fd (src/agent_plain_ingress.cpp:237)
   │  · 设置非阻塞 O_NONBLOCK
   │  · 受 max_sessions 总量约束（ingress sessions + 池内 sessions）
   ▼
main reactor 上的 ingress 状态机 (src/agent_plain_ingress.cpp)
   │  · 增量解析 16 字节 WireFrameHeader + payload，64 KiB 读预算 (kIngressReadBudget)
   │  · 阶段：WAIT_HELLO → SEND_HELLO_ACK → WAIT_OPEN
   │  · 认证（token 常量时间比较）在业务操作接受之前完成
   │  · session-open 超时定时器（逻辑阶段 1: accept→HELLO；阶段 2: ACK→首个操作）
   ▼
ingress_handoff (src/agent_plain_ingress.cpp:163)
   │  · 恢复阻塞模式 O_NONBLOCK off
   │  · 打包 agent_session_preface_t{max_frame, initial_window, peer_caps, first_open}
   │  · reactor_del + agent_session_pool_submit_prefaced()
   ▼
弹性会话池 (src/agent_session_pool.cpp)
   │  · --session-workers 是上限（ceiling），worker 按队列压力创建、idle 超时回收
   │  · 首个完整操作帧 + HELLO/认证结果随 preface 一并移交，worker 不重读 HELLO
   ▼
业务分发（TREE/FILE/System RPC/EXEC 设置）
   │
   └─ 仅 plain EXEC：第二次移交 → 共享 EXEC 事件域 (src/agent_exec_io_pump.cpp)
```

**两层 admission 约束是刻意分离的**（`src/agent_plain_ingress.cpp:239`、`src/agent_session_pool.cpp:171`）：

- `max_sessions` = ingress sessions + 池内 sessions（总连接槽）。
- `session_queue / session_workers` = 仅"完整可处理请求"（业务线程槽）。

未完成 HELLO/首帧的慢客户端可占连接槽，但不占业务 pthread。

### 2.2 TLS 路径：独立 Reactor 入口 + Reactor Group 分片

```text
listen fd
   ▼
agent_tls_runtime (src/agent_tls_runtime.cpp)
   ▼
reactor_group 选片：shard 0 先完成 TLS 握手 + HELLO
   │   · reactor_group_select_index (src/reactor_group.cpp:51)
   │   · bulk HELLO 后按 least-active 安全点移交到数据分片 (reactor_group_select_least_connections, :56)
   ▼
tls_reactor_conn_t (src/tls_reactor.cpp)
   │   · 非阻塞 TLS 状态机：HANDSHAKE/OPEN/DRAINING/SHUTDOWN/CLOSED/FAILED
   │   · 显式 WANT_READ/WANT_WRITE 重试归属（rx_wait/tx_wait/io_retry）
   │   · 每连接 pinned 到单一 shard，连接生命周期内不迁移
   ▼
Control / EXEC / Data Lane / TREE 各自 FSM
```

- **shard 亲和**：`reactor_group_select`（`src/reactor_group.cpp:43`）用 64 位混淆哈希（`key^=key>>33; key*=…`）保证确定性亲和；TLS 控制/数据连接按 group key 或 least-connections 选片。
- **TLS 无 per-connection pump 线程**：`tls_reactor_conn_t` 不拥有 pthread/mutex/cond/wake pipe/私有 Reactor，全部状态归所属网络 shard。

### 2.3 数据通道（Data Lanes）

大文件并行传输（`docs/DATA_LANES.md`，`src/agent_tls_data_lane.cpp`）：

- 控制连接管理 group 状态；每条 lane 独立 TCP/TLS 传输，按确定性范围 `pread()/pwrite()` 分片。
- TLS lane socket 归 Reactor shard；阻塞的 prepare/commit/cleanup 与常规文件 I/O 走有界 worker 池。
- 字节偏移恢复（resume）当前使用单 lane；sparse HOLE 帧与 SHA-256 保持逻辑文件语义。

### 2.4 System RPC 网络边界

`src/agent_system_service.cpp` 暴露稳定、类型化、受策略控制的操作，**不暴露 syscall 号**。所有文件系统 RPC 在 Agent `--root` 下解析，中间符号链接由 `openat/fstatat/O_NOFOLLOW` 解析器拒绝（`src/agent_system_service.cpp:59`），最终对象查询无 follow 语义，防止逃逸 root。突变操作需 `--enable-fs-mutate`。

### 2.5 客户端网络编排

- 普通命令走 `client_control_reactor`（TLS）或 `Connection` 同步路径。
- TLS put/get 大文件走 `client_data_lane_runtime`（`src/client_data_lane_runtime.cpp`，`kMaxDataLanes` 个 lane 线程）。
- EXEC 走 `client_blocking_exec`。
- 客户端本身可含 1 个 reactor（`client_control_reactor` 内置 `reactor_storage`）+ 有界 work pool（1 worker / 8 queue，`src/backupctl.cpp:1225`）。

## 3. 线程架构

项目线程模型的核心原则：**事件线程（Reactor）与阻塞工作线程（Work Pool / 会话池）分离，慢消费者只背压自身，不阻塞共享 shard**。

### 3.1 Agent（backup-agent）线程全景

| 线程/池 | 角色 | 源码 | 规模配置 |
|---|---|---|---|
| main reactor | accept + signal + **plain ingress** + backoff 定时器 | `src/backup_agent.cpp:997` | 1 个（无 TLS 时承载全部 plain 入口） |
| Reactor Group（TLS） | TLS 网络分片：握手/Control/Data Lane/EXEC FSM | `src/reactor_group.cpp` | `--network-reactors` N 个独立 reactor 线程 |
| 弹性会话池 | 非 TLS 业务 worker（TREE/FILE/System RPC/EXEC 设置） | `src/agent_session_pool.cpp` | `--session-workers` 上限，压力创建，`--session-worker-idle-ms` 回收 |
| EXEC 事件域 shard | 非 TLS EXEC 子进程 I/O + TX 多路复用 | `src/agent_exec_io_pump.cpp` | `--plain-exec-reactors`（auto = ceil(max-exec/64)，≤8，≤CPU） |
| control_pool | TLS 短 Control 工作 | `src/backup_agent.cpp:1041` | `--control-workers` |
| lane_pool | TLS Data Lane I/O | `src/backup_agent.cpp:1048` | `--lane-workers` |
| lane_cpu_pool | TLS Data Lane CPU 后处理 | `src/backup_agent.cpp:1055` | `--lane-cpu-workers` |
| tree_pool | TLS TREE 阻塞编排 | `src/backup_agent.cpp:1063` | `--tree-workers` |

TLS 模式下列出的各 pool 均基于 `work_pool_t`（有界 pthread 池），另叠 `storage_backend` 与 `cpu_scheduler` 作为 lane 调度器（`src/backup_agent.cpp:1089/1104`）。

**弹性会话池行为**（`src/agent_session_pool.cpp`）：

- worker 采用 detached pthread，`live_workers` 先发布再 `pthread_create`，失败则回退（`spawn_worker_locked`，:114）。
- 空闲 worker 用 `pthread_cond_timedwait` 等 `session_worker_idle_ms`（0 = 常驻，:51）；超时且队列空则自我退出（:59）。
- EXEC handoff 后 worker 立即退休，除非已有排队工作（:100）。

**EXEC 事件域 shard**（`src/agent_exec_io_pump.cpp`）：进程级共享事件域，shard 懒创建；一个 shard 复用子进程 stdin/stdout/stderr 管道、合并命令唤醒管道与 socket 可写性。每会话有界 TX 队列 + 独占非阻塞 `sendmsg` 路径；慢消费者只背压自身子管道。轻载 shard（≤4 会话）用更小预算。

### 3.2 客户端（backupctl）线程全景

| 线程/池 | 角色 | 源码 |
|---|---|---|
| main 线程 | CLI 编排、遍历、catalog 事务 | `src/backupctl.cpp` |
| Data Lane 线程 | TLS put/get 的 lane worker（`data_lane_client_thread`） | `src/backupctl.cpp:350` |
| 小文件本地写入线程 | small-file pack 的本地落盘 | `src/backupctl.cpp:970` |
| 内置 reactor + work pool | TLS 控制连接状态机（1 reactor + 1 worker/8 queue） | `src/backupctl.cpp:1223-1225` |

### 3.3 元数据自适应并行（v73）

目录枚举与 catalog/协议应用在主遍历线程有序；元数据探测先串行采样前 128 项，`fstatat(AT_SYMLINK_NOFOLLOW)` 均值 ≥50us 才启用**恰好 4 个** 128 KiB 栈 stat worker（`src/client_metadata_scan.cpp`），激活后同批内未采样后缀立即并行。worker 创建失败降级回串行，不导致备份失败。

## 4. 事件架构

事件架构以 `reactor_t`（epoll 事件循环）为核心原语，辅以通用事件等待器 `event_waiter_t`。

### 4.1 reactor_t：epoll 事件循环

`src/reactor.hpp:102` 定义 reactor 状态，含：

- **safe source identity**（token/generation，`src/reactor.hpp:67`）：`epoll_event.data.u64 = generation:32 | slot:32`。回调删除 source 后，同批 epoll 事件里的旧 token 无法解析即被丢弃，杜绝 UAF。
- **interest 更新合并（50.0）**（`src/reactor.hpp:117-122`）：`reactor_mod` 在回调执行期延迟 `EPOLL_CTL_MOD`，回调返回时按逻辑目标最多发一次 MOD；目标回到回调入口兴趣则不发；删除则取消挂起 MOD。
- **cross-thread posting**：`eventfd`（wakefd）唤醒；HIGH/NORMAL 双有界队列（`reactor_post_item_t`，`src/reactor.hpp:77-88`），HIGH burst 限流防 NORMAL 永久饥饿。
- **逻辑定时器**：单 timerfd + 最小堆 `timer_heap` + `timer_registry`（`src/reactor.hpp:129-130`）；业务代码只用轻量 `reactor_timer_t`，不做原始 timerfd。
- **回调预算**：`callback_budget`、`high_priority_burst`、`slow_callback_ns` 阈值与完整 metrics（`src/reactor.hpp:32-65`）。
- **owner 线程锁定**：`owner_tid` 原子记录；hot-path 连接状态在单 shard 内无锁。

事件循环流程：`epoll_wait` → 按 token 解析 source → 执行回调（受预算约束）→ 处理 post 队列（HIGH 优先、burst 后放 NORMAL）→ timer 到期回调。

### 4.2 event_waiter_t：通用等待原语

`src/event_wait.hpp:30`，epoll/poll 双后端（`EVENT_BACKEND_AUTO/POLL/EPOLL`）。用于：

- **backup-dirtyd**：inotify 事件等待（`src/backup_dirtyd.cpp:205`）。
- **EXEC 事件域 shard**：子进程管道 + 唤醒管道的多路复用（`src/agent_exec_io_pump.cpp:862`）。
- **v78 pidfd 等待**：内核支持时用 pidfd + event_waiter 等子进程退出与 socket RX；否则回退 100ms 轮询。

### 4.3 work_pool_t：有界阻塞工作池

`src/work_pool.hpp:124`。有界 pthread 池，承载 epoll 无法异步化的阻塞操作（open/stat/getdents、pread/pwrite、fsync、SQLite/LMDB、CPU hash）。完成回调通过 `reactor_post()` 回到**提交时的所属 shard**（`work_item_t::completion_reactor`，`src/work_pool.hpp:104`）。支持公平性（fair key/class）与按 metric class 的延迟直方图统计。

### 4.4 事件流转的层叠图

```text
              fd 就绪
                 │
      ┌──────────┴──────────┐
      │      epoll          │
      └──────────┬──────────┘
                 ▼
           reactor_t (owner thread)
      ┌──────────┼──────────────────┐
      │          │                  │
 ingress   TLS Reactor       EXEC event shard
 状态机     状态机               (event_waiter_t)
      │          │                  │
      └──────────┼──────────────────┘
                 │ 阻塞工作提交
                 ▼
            work_pool_t
                 │ 完成回调
                 ▼
       reactor_post(原 shard) ← eventfd 唤醒
```

### 4.5 慢消费者背压模型

- plain ingress：64 KiB 读预算，单连接不能独占 main reactor。
- Control dispatcher：128 通道暂停 RX / 64 恢复（inflight 门限），无条件变量阻塞 Reactor 线程。
- EXEC shard：慢消费者只暂停自身子管道背压，不动 shard。
- TLS 连接：TX high/low water 控制加密输出排队；EAGAIN 时保留响应游标、经 `on_writable` 恢复。

## 5. 关键路径（源码级）

### 5.1 连接接受 → ingress → 会话池 → EXEC 移交（plain）

```
① reactor_add(listen fd, agent_acceptor_listener_cb)   src/backup_agent.cpp:1171
② agent_acceptor_listener_cb: accept burst≤64          src/agent_acceptor.cpp:29
③ agent_accept_submit → 非 TLS: agent_plain_ingress_submit_fd  src/backup_agent.cpp(agent_accept_submit)
④ ingress 非阻塞解析 HELLO → 认证 → HELLO_ACK → 首个操作帧  src/agent_plain_ingress.cpp:194 (ingress_source_cb)
⑤ ingress_handoff: 恢复阻塞 + preface + 提交会话池         src/agent_plain_ingress.cpp:163
⑥ 会话池 worker: session_main → 业务分发                 src/agent_session_pool.cpp:41
⑦ plain EXEC: agent_exec_start_handoff → 共享事件域       src/agent_exec_runtime.cpp (agent_exec_start_handoff)
⑧ EXEC shard 多路复用子进程管道/socket                    src/agent_exec_io_pump.cpp
```

### 5.2 TLS 连接路径

```
① accept → agent_tls_runtime → reactor_group 选片(shard 0)  src/agent_tls_runtime.cpp
② TLS 握手 (tls_reactor_conn_t 状态机) + HELLO              src/tls_reactor.cpp
③ bulk HELLO → least-active 数据 shard 安全点移交            src/reactor_group.cpp:56
④ Control/EXEC/Data Lane/TREE FSM 在所属 shard 上          docs/CONTROL_REACTOR.md
```

### 5.3 备份目录批处理（客户端数据面，非网络热路径）

目录队列 + getdents64 游标分批（`src/client_backup_state.cpp`），每 256 项 checkpoint；TREE 事务以 `TREE_BARRIER`/`FF_DIR_FINAL` 累积 ACK 为栅栏（`docs/ARCHITECTURE.md`）。非最终批 checkpoint 顺序严格为：发送条目 → 远端状态变更 ACK → 校验源目录身份 → 提交 catalog 批 → 提交目录游标。

## 6. 存储/数据架构概述（上下文）

- **权威 catalog**：client-owned，`path→inode / inode→metadata / parent+name→child`，SQLite（默认）或 LMDB（可选，`--enable-lmdb`）。提交批次为临时态，最终 generation 发布原子清除 `active_run` 栅栏。
- **backup-state**：持久化目录队列（PENDING/PROCESSING/DONE）+ 源目录身份 + getdents64 游标 + dirty hint；未启用 resume 时用 unlink-on-open 临时 SQLite 保持内存有界。
- **restore-state**：catalog 驱动的有界/可恢复恢复。
- **hardlink 追踪**：compact 索引 + 磁盘溢出页；committed nlink>1 才记录。
- **大文件 resume**：≥`--resume-large-threshold` 保留字节偏移 partial；小文件中断即丢弃随目录重放。

## 7. 既有文档滞后差异清单

| # | 文档断言（旧） | 80.0.0 源码现状 | 差异 |
|---|---|---|---|
| 1 | `NETWORK_MODEL.md:141` "plain-TCP sessions" 仍属同步兼容路径 | plain 连接在握手/认证/首操作阶段已由 `agent_plain_ingress` 事件化（v80，`src/agent_plain_ingress.cpp`），仅**业务处理**仍走阻塞会话池 | 部分过时（ingress 段已迁移） |
| 2 | `NETWORK_MODEL.md:93` "shard 0 owns TLS ingress/control" | TLS 入口确实经 shard 0，但 v80 后 plain 入口走 main reactor 上的 `agent_plain_ingress`，与 TLS 分片无关 | 需补充 plain 路径说明 |
| 3 | `REACTOR.md:1` 标题标注 "— 30.0" | 实际实现已含 50.0 的 interest 合并、28.0 唤醒合并、40+ 轮演进 | 版本标注滞后 |
| 4 | `NETWORK_MODEL.md:1` 标题标注 "— 30.0" | 网络模型已演进到 v80 plain ingress + 弹性池 + 共享 EXEC 域 | 版本标注滞后 |
| 5 | `CONTROL_REACTOR.md:123` "plain-TCP server sessions" 属同步路径 | v80 后 plain 握手段异步，仅业务段同步 | 部分过时 |
| 6 | `ASYNC_CALLBACK_MODEL.md:1` 标 "9.0" | 回调运行时已扩展到 ingress/EXEC 域/pidfd，远超 9.0 基线 | 版本标注滞后 |
| 7 | `NETWORK_MODEL.md:141` "streaming READDIR bounded Reactor producer" 归入未迁移 | v73+ 客户端元数据探测已支持并行 stat worker（`src/client_metadata_scan.cpp`） | 需补充 |

**结论**：`NETWORK_MODEL.md`、`REACTOR.md`、`ASYNC_CALLBACK_MODEL.md` 是演进历史文档，标注版本低于当前实现。`ARCHITECTURE.md`、`DATA_LANES.md`、`TLS_REACTOR.md`、`SYSTEM_RPC.md` 与 80.0.0 基本一致，可作为当前事实参考。本报告与源码一致，作为 80.0.0 的统一实现视图。

## 8. 参考资料

- `src/reactor.hpp|cpp`、`src/reactor_group.cpp`、`src/work_pool.hpp|cpp`
- `src/event_wait.hpp|cpp`、`src/agent_plain_ingress.cpp`、`src/agent_session_pool.cpp`
- `src/agent_acceptor.cpp`、`src/agent_exec_io_pump.cpp`、`src/agent_exec_runtime.cpp`
- `src/agent_tls_runtime.cpp`、`src/tls_reactor.cpp`、`src/agent_system_service.cpp`
- `src/backup_agent.cpp`、`src/backupctl.cpp`、`src/backup_dirtyd.cpp`
- `docs/ARCHITECTURE.md`、`docs/NETWORK_MODEL.md`、`docs/ASYNC_CALLBACK_MODEL.md`、`docs/REACTOR.md`、`docs/CONTROL_REACTOR.md`、`docs/TLS_REACTOR.md`、`docs/DATA_LANES.md`、`docs/SYSTEM_RPC.md`
- `docs/ROUND80_REVIEW.md`、`README.md`
