# 跟进：统一 RPC fd-only 与 session mTLS 数据面并补真实回归

## 问题陈述

- **现状**：RPC 同时存在返回裸 fd 的连接接口和携带 SSL/读写函数的 session 接口；mTLS 协商成功时 fd-only API 当前直接失败，多个业务入口仍使用 fd-only 收发。
- **目标**：所有受 mTLS 配置影响的 RPC 业务路径都使用同一个 session transport，并补充真实进程回归证据。
- **差距**：连接对象所有权、cleanup、超时和应用帧测试尚未统一。

## 解决方案

以 session transport 作为 RPC 连接的唯一数据面，迁移可达业务入口，统一 SSL/fd 生命周期；补齐握手严格校验、超时和真实 RPC/rdbcomm 测试矩阵。保留既有配置参数，不新增客户端参数，不兼容旧协议。

## Seam 分析

### 测试接缝

### 声明的测试接缝
- seam: libs/tests/rpc_handshake_test.c -> libs/rpc-handshake.c
- seam: rpc/tests/download_file.cpp -> rpc/rpc-io.cpp, rpc/rpc-server.cpp
- seam: rpc/tests/execute_command.cpp -> rpc/rpc-io.cpp, rpc/rpc-server.cpp
- seam: rpc/tests/mtls_integration.cpp -> rpc/rpc-io.cpp, rpc/rpc-server.cpp
- seam: rdbcomm/tests/mtls_integration.c -> rdbcomm/client.c, rdbcomm/server.c

## 验收标准

- [ ] AC-1: mTLS 协商成功后所有受影响 RPC 业务入口均通过 session transport 收发，不再依赖裸 fd。
- [ ] AC-2: RPC 服务端、客户端和 rdbcomm 所有 SSL 成功/失败/关闭路径无未释放 SSL 或重复关闭 fd。
- [ ] AC-3: 握手响应严格校验 operation/version/result，错误帧返回可区分的错误码，并有超时边界。
- [ ] AC-4: 真实 RPC/rdbcomm 进程测试覆盖明文、常规 mTLS、SM2 mTLS、算法不匹配、证书缺失和服务端强制 mTLS 不降级。
- [ ] AC-5: 既有 RPC/rdbcomm 业务回归和时间获取功能通过，且不新增客户端配置参数。

## 范围外

- 不实现旧协议兼容。
- 不改造 SBT、UI、存储加密和无关业务。
