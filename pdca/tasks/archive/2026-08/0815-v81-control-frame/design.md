# v81 后续控制帧非阻塞化 — design

## 现状分析

### v80 plain 会话生命周期
```
accept -> ingress 非阻塞解析 HELLO/auth/HELLO_ACK/首操作帧
       -> handoff: fd 转阻塞, 交 session_pool 弹性 worker
       -> session_main -> session_dispatch_loop 阻塞 recv 循环处理所有后续帧
```

**瓶颈**：`session_dispatch_loop` 在 worker 线程内阻塞 `connection_recv_frame_timeout`。客户端发送一个完整操作后停顿，worker 全程占死。256 个 stalled 连接 = 256 个 worker（v79 实测 33 线程）。

### TLS 控制面蓝图（可复用）
`agent_tls_control_runtime.cpp`：
- Reactor 持有 fd，`agent_tls_control_submit` 收帧
- 每帧建 job：`work_item_init` + `work_pool_submit`（`WORK_METRIC_CONTROL`）
- worker `control_job_run` 执行生成 responses vector
- `control_job_done`（reactor 线程）经 `tls_reactor_send_frame` 回发
- inflight high/low 限流、`RX_PAUSE`/`RX_CONTINUE` 背压

## 方案

### 目标架构（v81 plain 控制面）
```
accept -> ingress 非阻塞解析 HELLO/auth
       -> 持续持有 fd, 非阻塞解析后续控制帧
       -> 每完整 work-ready 帧封装 work item -> work_pool
       -> worker 执行 -> done 回调(reactor) -> 非阻塞 TX 回发
       -> TREE/FILE/EXEC 等需整会话的帧 -> 仍走 v80 handoff
```

### 关键设计点

1. **ingress 会话生命周期扩展**：认证后不 handoff，进入持续控制分派态。仅当遇到 TREE/FILE/EXEC 等需要整 fd 的操作类型时 handoff。
2. **work-ready 判定**：单帧请求-响应类操作（PING、TIME_REQ、SYS_REQ 等，参照 `service_is_control`）进入 work-ready 分派。
3. **work item 生命周期**：ingress 会话内管理 pending job；worker 完成 → reactor post 回发 → 释放。
4. **会话有序**：单会话按帧到达顺序分派；多会话并行但每会话串行（参照 TLS control jobs map by channel）。
5. **能力位**：新增 `CAP_PLAIN_CONTROL_ASYNC`。仅当 peer 支持时才启用；否则整 fd handoff（v80 行为）。
6. **背压**：ingress TX 有界（复用现有 tx 缓冲）；work_pool 有界队列满时按 EBUSY 拒绝并回发错误。

### 模块改动
- `src/agent_plain_ingress.hpp/.cpp`：增加 work-ready 分派路径、work_pool 引用、job 管理。
- `src/agent_config.hpp/.cpp`：新增能力位定义。
- `src/backup_agent.cpp`：plain 模式初始化 work_pool 并传给 ingress。
- `tests/v81_control_frame_integration.sh`：新增回归。

### 不变量
- 协议 RSP/3 帧类型/字节布局不变。
- 每会话帧序保持。
- 未认证/未完整首帧的连接不消耗业务 worker（v80 既有保证保留）。
- TREE/FILE/EXEC 行为与 v80 完全一致。

## 验收映射
- AC-4: v81 回归脚本（分片后续控制帧重构+分派+有序）
- AC-5: 慢客户端不占 worker
- AC-6: 数据面并发不回归
- AC-7: 跨版本互操作
- AC-8: 线程数降≥50%、RSS 不升
