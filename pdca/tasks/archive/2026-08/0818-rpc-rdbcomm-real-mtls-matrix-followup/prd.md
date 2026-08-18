# 跟进：完成 RPC/rdbcomm 真实 mTLS 工具矩阵与时间测试

## 问题与目标

T0310 已完成 RPC 业务层 session-only 迁移和基础回归，但真实工具层尚未证明 mTLS 密文数据面、CA-CN 证书选择、算法失败、强制 mTLS 不降级及 TIME-only 场景。T0312 只补测试和必要的现有命令行为，不新增客户端配置参数。

## 范围

- 使用 `tls-keygen` 生成测试 CA、服务端证书及多个客户端证书目录，验证服务端返回 `ca_cn` 后客户端选择正确证书。
- 真实启动 `aio-speedd`/`aio-speed` 与 `rdbcommd`/`rdbcomm`，覆盖明文、classic mTLS、SM2 mTLS、算法不匹配、证书缺失、服务端强制 mTLS 禁止降级。
- 使用独立 `time` 子命令触发 TIME-only；验证 TIME 后连接关闭，不能进入应用第二阶段。
- 所有测试目标通过 `add_tests("default")` 接入 `xmake test`。

## 非范围

- 不兼容旧协议。
- 不新增客户端参数或隐式 fd→session 适配层。

## 验收标准

- [ ] AC-1: 测试使用 tls-keygen 生成可复现的 CA、服务端证书和至少两个客户端证书目录，并证明服务端返回的 `ca_cn` 选择了正确客户端证书。
- [ ] AC-2: 真实 RPC/rdbcomm 工具进程完成明文、classic mTLS、SM2 mTLS 的应用数据帧往返，mTLS 应用数据始终通过 TLS session 收发。
- [ ] AC-3: 真实工具测试覆盖算法不匹配、客户端证书缺失、服务端强制 mTLS 时客户端明文降级三类失败，并断言明确错误和连接关闭。
- [ ] AC-4: RPC 与 rdbcomm 通过独立 `time` 子命令完成 TIME-only 时间获取，收到时间后连接关闭且不会进入第二阶段。
- [ ] AC-5: 所有新增测试均注册到 `xmake test`，定向和全量测试通过，不新增客户端配置参数。

## 设计决策

- 测试进程由编译后的测试二进制 fork/exec 管理，使用临时目录和动态端口。
- 测试证书目录按服务端返回的 `ca_cn` 建立；错误场景使用独立临时证书目录，避免污染仓库证书。
- 算法选择复用现有 `RPC_TLS_CIPHERSUITES` 配置，不增加参数；classic/SM2 的差异由现有环境配置驱动。

## Seam 分析

### 声明的测试接缝

- seam: `rpc/tests/tool_mtls_integration.cpp` -> `rpc/main.cpp`, `rpc/rpc-client.cpp`, `rpc/rpc-server.cpp`, `libs/tls_cert.c`
- seam: `rdbcomm/tests/tool_mtls_integration.c` -> `rdbcomm/rdbcomm-main.c`, `rdbcomm/client.c`, `rdbcomm/server.c`, `libs/tls_cert.c`
- seam: `rpc/tests/time_integration.cpp` -> `rpc/rpc-client.cpp`, `libs/rpc-handshake.c`
- seam: `rdbcomm/tests/time_integration.c` -> `rdbcomm/rdbcomm-main.c`, `rdbcomm/client.c`, `libs/rpc-handshake.c`
- seam: `libs/tests/rpc_handshake_test.c` -> `libs/rpc-handshake.c`, `libs/tls_cert.c`

## 任务拆解

1. 明确现有 `-c/--cmd` 的 TIME 入口和协议行为，先补红测。
2. 用 tls-keygen 建立临时多证书 fixture，补 CA-CN 选择测试。
3. 实现真实 RPC/rdbcomm classic/SM2 工具矩阵和失败矩阵。
4. 将所有测试目标接入 `xmake test`，运行全量验证并登记 evidence。

## 备注

`task_identity` 创建记录：2026-08-18T14:50:30+08:00。
