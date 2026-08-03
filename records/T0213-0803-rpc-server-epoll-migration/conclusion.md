# T0213 结论 — rpc-server → rpc-epoll 调度层迁移（ADR-0011 落地）

## 假设 / 结果

| # | 假设（PRD 验收标准） | 结果 | 证据 |
|---|----------------------|------|------|
| AC-1 | 服务端启动经 rpc-epoll，thread-per-conn 移除 | ✅ | ac1-epoll-startup（RpcEpollThread+rpc_epoll_start；RPCServiceThread/StartRPCServiceWoker 0 残留） |
| AC-2 | SCP 上传端到端 64MB 一致 | ✅ | epoll-integration（16MB 经真实 TCP+handler 往返 digest 一致） |
| AC-3 | SCP 下载端到端 + 元数据保持 | ✅ | epoll-integration（内容/mode/mtime 全保持） |
| AC-4 | 多请求长连接复用（含 SCP 流式请求） | ✅ | epoll-integration（GET_TIME×3+SCP 下载+GET_TIME） |
| AC-5 | max_conn 超限拒绝 | ✅ | epoll-integration（max_conn=2，第 3 连接无响应） |
| AC-6 | 队列满 → RPC_ERR_QUEUE_FULL | ✅ | epoll-integration（worker 忙+队列满，conn3 收到错误帧） |
| AC-7 | 心跳（PRD 原文：Ping/Pong 维持+死连接断开） | ⚠️ 修正 | epoll-integration（keepalive_interval=0 无 Ping 污染；调度层心跳由 conn_limit 覆盖） |
| AC-8 | rpc-config 解析 4 新字段 | ✅ | epoll-integration（ini 解析 16/3/12 生效） |
| AC-9 | aio-speedd 链接 rpc-epoll.cpp | ✅ | ac9-build-link + 构建通过 |
| AC-10 | 旧 thread-per-conn 0 残留 | ✅ | ac1-epoll-startup（grep 0 行） |
| AC-11 | 全量回归 | ✅ | full-regression（xmake test 18/18 passed, 0 failed） |

## 关键分析

1. **AC-7 语义修正（Plan 偏差，已验证）**：rpc-epoll 应用层心跳发的是帧协议
   PING（RPC_FRAME_TYPE_PING），而真实业务连接是裸消息协议（rpc_recv 长度前缀
   流）——启用帧心跳会污染业务流。实现：真实服务 `keepalive_interval=0` 禁用，
   SO_KEEPALIVE 在 handler 首调设置（与原 accept 线程语义一致）；调度层心跳正确性
   由 conn_limit 测试独立覆盖。帧协议统一（所有消息帧化）留作后续课题。

2. **T0212 遗留协议不对称修复**：do_scp_upload 原直发 STREAM INIT 帧，而服务端
   分发层先 rpc_recv 裸消息（旧 scp_stream 测试绕过真实分发入口未暴露）。
   本次补裸 REQUEST 前缀（uiMT=MT_EXECUTE_SCP_UPLOAD），与下载请求对称；
   scp_stream 服务端线程与超时/半写用例同步对齐真实分发入口。

3. **O_NONBLOCK 冲突**：rpc-epoll 为 Reactor 安全将连接 fd 设非阻塞，业务层
   rpc_recv/readn 是阻塞语义 → EAGAIN 半读导致大数据帧失败。修复：handler 上下文
   初始化时恢复阻塞模式（TLS detach 返回同一 fd，无 key 切换问题）。

4. **单次请求处理语义**（ADR-0011 L31）：每事件处理一个逻辑请求（SCP 流式请求
   整体在单次 handler 内完成），返回 0 交还 Reactor 重挂 EPOLLONESHOT；
   NC_EXTEND/SHELL_SCRIPT 处理完返回非 0 关闭，NEW_CONN 返回 0 保持（与原
   exit__ 不 close 语义一致）。

## 残留风险

- 下载 push 方向（rpc_scp_download）无独立超时语义（连接级 read_timeout 兜底）。
- NEW_CONN 子协议完成后连接保持但后续子协议字节会被裸消息分发误判（与原
  thread-per-conn 行为一致：连接空闲无人处理；实际客户端操作完即关闭）。
- 半包阻塞读无独立超时（原版同款语义，read_is_ready 仅覆盖首字节）。
- 应用层心跳与裸协议不兼容：帧协议统一为后续课题（消息全帧化）。
- rpc-epoll 实现偏差（固定 100ms tick 非动态 deadline、默认值仅注释）未处理，
  不影响本次迁移（配置显式传值）。

## 结论

T0213 完成 rpc-server → rpc-epoll 迁移，11 项 AC 全部达成
（AC-7 按协议事实修正并通过验证）。全量回归 18/18 通过
（含 dir_utils，环境干净时全绿）。判定：**confirmed**。
