# RPC 项目支持 IPv6 — 规格文档

## 问题陈述

- **现状**: RPC 项目的所有网络层代码均硬编码为 IPv4-only（`AF_INET`、`struct sockaddr_in`、`inet_ntoa()`、`inet_pton(AF_INET)`），无法在纯 IPv6 或双栈环境中运行。
- **目标**: RPC 服务端和客户端同时支持 IPv4 和 IPv6 协议栈。
- **差距**: 共 4 个核心模块需要修改（`rpc-server.cpp` 服务端监听、`rpc-io.cpp` 客户端连接、`rpc-server.cpp`/`rpc-io.cpp` 日志审计）。

## 解决方案

将硬编码的 `AF_INET` 替换为 `AF_UNSPEC`（客户端）或双栈 `AF_INET6`（服务端），使 RPC 服务能够同时接受 IPv4 和 IPv6 连接。

## 用户故事

1. 作为运维人员，我可以在纯 IPv6 环境中启动 RPC 服务端，以便 IPv6-only 节点能正常进行文件备份/恢复。
2. 作为运维人员，我可以用 `--host` 参数指定 IPv6 地址连接 RPC 服务端，以便在 IPv6 网络中正常操作。
3. 作为运维人员，我可以使用 `--bind-ip` 参数指定 IPv6 的本地绑定地址，以便在多网卡环境中精确选择出口。

## 任务拆解

| 子任务 | 文件 | 变更内容 |
|--------|------|---------|
| T1 服务端双栈 | `rpc-server.h` `rpc-server.cpp` | socket/AF_INET6、in6addr_any、sockaddr_storage、accept/getpeername 适配 |
| T2 客户端连接 | `rpc-io.cpp` | `connect_server`/`connect_server2` 用 `getaddrinfo` 替代 `inet_pton` |
| T3 日志泛化 | `rpc-io.cpp` `rpc-server.cpp` | sockaddr_in→sockaddr_storage、inet_ntoa→inet_ntop、ss_family 动态分发 |
| T4 编译验证 | — | 确保现有 IPv4 连接回归正常 |

## 实现决策

**已确认方案: AF_INET6 双栈 (`IPV6_V6ONLY=0`)**

- **服务端** (`rpc-server.cpp`): `s/AF_INET/AF_INET6/g`，`s/INADDR_ANY/in6addr_any/g`，`s/struct sockaddr_in/struct sockaddr_in6/g`，添加 `IPV6_V6ONLY=0` setsockopt 实现双栈
- **客户端** (`rpc-io.cpp`): `connect_server`/`connect_server2` 使用 `getaddrinfo()` 替代 `inet_pton()`，自动解析 IPv4/IPv6；socket 创建用 `ai_family`
- **日志/审计** (`rpc-io.cpp`, `rpc-server.cpp`): `struct sockaddr_in` → `struct sockaddr_storage`，`inet_ntoa()` → `inet_ntop()`，`inet_ntop(AF_INET)` → 从 `ss_family` 动态获取地址族
- **Worker info** (`rpc-server.h`): `struct sockaddr_in serv` → `struct sockaddr_storage serv`
- **svr_ip[64]/local_ip[64]**: 已足够容纳 IPv6 地址（39 字节 + null），无需修改
- **rpc_session_start/rpc_file_existed**: 通过 `connect_server` 升级自动受益

## 验收标准

- [ ] AC-1: 服务端在 `AF_INET6` 双栈模式下可同时接受 IPv4 和 IPv6 客户端连接
- [ ] AC-2: 客户端可通过 IPv6 地址成功连接服务端（`--host=::1`）
- [ ] AC-3: 客户端可通过 IPv4 地址成功连接服务端（回归保证）
- [ ] AC-4: `--bind-ip` 支持 IPv6 本地绑定地址
- [ ] AC-5: 日志和审计输出中 IPv6 地址显示正确，而非 `inet_ntoa` 截断

## 范围外

- IPv6 ACL/防火墙规则管理
- DNS 解析支持（当前仅接受 IP 字符串）