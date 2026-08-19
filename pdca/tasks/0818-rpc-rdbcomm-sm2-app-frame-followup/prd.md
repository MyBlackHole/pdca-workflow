# 跟进：修复 rdbcomm SM2 真实应用帧握手失败

## 问题陈述

SM2/TLS_SM4_GCM_SM3 的证书初始化已成功，但真实 rdbcomm 应用请求在第一阶段之后失败；当前日志不足以定位是证书验证、密码套件协商还是 TLS session 切换问题。

## 解决方案

补充可诊断的 TLS 握手错误信息，修复真实 rdbcomm 的 SM2 mTLS session 进入应用数据面的路径，并用 RPC/rdbcomm 工具进程验证密文应用帧往返。保持现有配置项和独立 `time` 子命令。

## Seam 分析

### 声明的测试接缝

- seam: `rdbcomm/tests/tool_integration.c` -> `rdbcomm/rdbcomm-main.c`, `rdbcomm/client.c`, `rdbcomm/server.c`, `libs/tls_cert.c`
- seam: `rpc/tests/time_integration.cpp` -> `rpc/rpc-client.cpp`, `rpc/rpc-server.cpp`, `libs/rpc-handshake.c`
- seam: `libs/tests/tls_cert_test.c` -> `libs/tls_cert.c`

### 验收可测性

通过真实进程退出码、应用响应、服务端日志中的握手/错误信息以及全量 `xmake test` 判定；不直接测试私有函数。

## 实现决策

- 复用既有 SM2 证书和 `RPC_TLS_CIPHERSUITES` 配置，不增加客户端参数。
- 诊断输出必须包含 OpenSSL 错误队列和协商结果，但不输出私钥或敏感配置。
- TLS 成功后业务读写只能使用绑定在握手结构体上的 session I/O。

## 验收标准

- [ ] AC-1: 运行真实 rdbcommd/rdbcomm SM2 mTLS 应用测试，得到成功的应用请求和响应，且日志确认使用 `TLS_SM4_GCM_SM3`。
- [ ] AC-2: 运行真实 RPC TIME/classic mTLS 回归以及 rdbcomm SM2 mTLS 应用帧测试，均保持既有行为并不使用 `-c time`。
- [ ] AC-3: 运行证书缺失、算法不匹配和服务端强制 mTLS 明文降级测试，均得到非零退出、明确错误并关闭连接。
- [ ] AC-4: 运行 `xmake test`，所有已注册测试通过，且生产 CLI 参数集合不增加。

## 范围外

- 不兼容旧协议。
- 不新增客户端参数。
- 不把 TLS 应用帧退回裸 fd，也不改造 GMSSL/TLCP 后端。

## 备注

T0312 的 AC-2 因 SM2 真实 rdbcomm 应用帧失败而 partial；本任务只处理该缺口。
