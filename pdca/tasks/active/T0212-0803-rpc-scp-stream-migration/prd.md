# PRD — SCP 业务流式化 + rpc-server 调度层迁移（T0212 跟进）

> 来源：T0211 conclusion.md「下一轮建议」；parent: T0211

## 问题陈述

T0211 已交付 rpc 协议/传输层基础设施（帧协议、STREAM 流帧原语、心跳、错误码、
rpc-epoll 调度层），但生产路径尚未接入：

1. `do_scp_upload` / `do_scp_download` 仍走旧消息格式（512KB 块 + msg_scp_upload_t），
   STREAM 帧原语未用于实际业务流
2. `rpc-server.cpp` 仍为 thread-per-conn 模型（RPCServiceThread），未迁移到
   rpc-epoll 调度层（max_conn / 有界队列约束未作用于生产路径）
3. AC-15 的「服务端超时执行返回 RPC_ERR_TIMEOUT」依赖业务接入 INIT timeout_ms

## 目标

1. SCP 上传/下载改为 STREAM 帧序列（INIT/DATA/END），客户端服务端成对改造，
   保持断点续传语义
2. rpc-server 接入 rpc-epoll 调度层，thread-per-conn 移除或降级
3. 补 AC-15 服务端超时执行测试 + 业务层吞吐对比（AC-11 基准 514 MB/s）

## 验收标准（草案）

- 上传 1GB 文件经 STREAM 流帧往返校验一致（sha256）
- 断点续传回归通过（中断后 offset 恢复）
- 服务端超时（timeout_ms）返回 RPC_ERR_TIMEOUT + 详情
- 业务层吞吐 ≥ 协议原语层 80%
- 并发 N 连接受 max_conn/有界队列约束（复用 conn_limit 断言模式）

## 范围外

- 不改变帧头协议（16B 头、8MB 上限已在 T0211 冻结）
- 不迁移非 SCP 命令（stat/rm/mkdir 等单帧命令保持现状）

## 依赖

- T0211 交付的 rpc/rpc-msg.h/c、rpc/rpc-epoll.h/cpp
- 知识：debugging/c-buffer-api-size_t-frame-validation.md
