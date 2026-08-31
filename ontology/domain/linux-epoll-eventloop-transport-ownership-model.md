---
schema: pdca.asset/v1
id: ontology:domain/linux-epoll-eventloop-transport-ownership-model
type: domain
layer: Knowledge
status: active
summary: 并发安全的传输所有权组织方法论：两容器 + 一抽象 + 一契约
domain:
- ontology:domain/linux-epoll-eventloop
relations:
  specializes:
  - ontology:domain/linux-epoll-eventloop
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 并发安全的传输所有权组织方法论：两容器 + 一抽象 + 一契约

来源: records/T0299-0816-transport-ownership/conclusion.md
对象: backupstream v101（agent_plain_ingress / tls_reactor / agent_tls_runtime）

## 核心模式：每个时刻每个对象恰属一个执行上下文

并发安全不依赖锁，而依赖**所有权归属的单一化**——把「谁拥有连接」拆成三个互不重叠
的维度，任何时刻在每个维度上恰有一个归属，并在维度间用显式转移点连接。

### 三类所有权（判定方法）

| 维度 | 含义 | 判定方法 |
|------|------|---------|
| Socket 所有权 | 谁负责 `::close(fd)`/`SSL_free()`、把 fd 注册进事件循环 | 找 fd/SSL 的**唯一释放点** |
| 协议状态所有权 | 谁拥有帧解析器、发送队列、FSM 状态机 | 找**帧分发入口** |
| 阻塞工作所有权 | 谁执行阻塞的磁盘/计算操作 | 找 `work_item.completion_reactor` |

### 两容器：socket 只落在两个地方

- plain 路径：session 直接持裸 `int fd` + source + tx 缓冲，解析/发送内联（无独立传输对象）。
- TLS 路径：独立 `tls_reactor_conn_t` 持 `fd + SSL*` + 双 tx 队列，`require_owner()` 强制
  所有 API 在 owner 线程运行（否则 EPERM）；业务层通过回调访问，**从不拥有 fd/SSL**。
- 核心原则：**传输对象要么是裸 fd 归属者，要么是 SSL+队列归属者；两者都不允许第三方 close。**

### 一抽象：业务 FSM 一律是租借者

业务 FSM（TREE/FILE/RESTORE/Lane/EXEC/Control）通过 transport adapter（函数指针表 + user）
借用 socket，不拥有。adapter 提供统一契约，双径同构实现：

- `emit_frame / send_fn / try_send / try_send_take`（发送 + 背压分级 + 缓冲转移）
- `resume_rx / tx_bytes / tx_can_accept / request_close`（暂停恢复 + 排空判定）
- `buffer_acquire / buffer_recycle / frame_headroom / native_fd`（缓冲管理 + fd 只读借用）

收益：**同一套业务 FSM 可被两类传输驱动**，双径只差 adapter 实现与 socket 容器。

### 一契约：阻塞工作经 completion_reactor 回穿

`work_item_t.completion_reactor`（work_pool.hpp:126）记录回穿目标；worker 线程完成后
`reactor_post_wait_priority(completion_reactor, NORMAL, work_completion_post, item)`
把结果 post 回 reactor 线程，由 `work_completion_post` 执行 `item->done`。
**不变量：worker 不碰业务状态，状态只在 reactor 线程改。**

### 转移点的并发安全契约（枚举范式）

每个转移点必须回答四个问题：转移前所有权 / 转移后所有权 / 转移原子性 / 失败回滚。
backupstream 的关键转移点（含契约要点）：

| 转移 | 契约 |
|------|------|
| ingress → 业务 FSM | 帧在 reactor 线程解析后同步转交；完成回调回穿同一 reactor |
| FSM → work pool 提交 | `work_item_init` 记录 completion_reactor；done 只在 reactor 线程执行 |
| work pool → FSM 回穿 | `reactor_post_wait_priority`；worker 不碰业务状态 |
| **plain EXEC → 共享事件域** | 先 `reactor_del` 摘 source（原 owner 不再碰 fd）→ `adopt_fd` → 转移 → erase 防复查 → delete 旧 session |
| LANE_ATTACH → lane FSM | lane fd 只取数值做注册键；storage 完成回穿 completion_reactor |
| TLS shard 间 handoff | 安全点语义：OPEN + rx_paused + 非 closing + 非 renegotiating；失败回滚原 owner |

## 陷阱与边界

- **EXEC 归属双径分化**：plain 转移 Connection 给独立共享事件域（多核承载 exec 并发）；
  TLS 留在原 reactor（已分片，避免二次转移成本）。**不要默认两者行为一致**。
- **销毁先摘除可观测性**：handoff 先 `reactor_del` 再转移，防悬挂事件；一次 close 通知
  （`close_notified`/`session_closed`）防重入销毁。
- **一次性通知**：所有「完成/关闭」回调都必须防重入。
- **fd 借用只读**：`native_fd` 返回值只能作注册键，绝不可 close，否则 double-close。

## 验收信号

- 能找到每个 fd/SSL 的唯一释放点 → socket 所有权清晰。
- 传输对象加一层 adapter 后业务 FSM 无感知 → 抽象有效。
- worker 线程代码不触碰任何业务状态字段 → 回穿契约成立。
- 每个转移点都能回答「转移前/后所有权 + 原子性 + 回滚」→ 边界可靠。