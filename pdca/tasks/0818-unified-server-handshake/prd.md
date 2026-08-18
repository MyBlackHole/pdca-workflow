# 统一 RPC/rdbcomm 服务端 mTLS 握手入口

## 问题陈述

RPC 与 rdbcomm 服务端分别实现首帧读取、时间请求处理、协商响应和 mTLS 升级，逻辑重复。后续多个工具接入 mTLS 时会继续复制代码，导致明文/mTLS 策略和错误处理不一致。

## 目标

在 `rpc-handshake.c/.h` 提供无回调、参数传递式的公共服务端首阶段入口，统一支持时间终止、明文继续、mTLS 升级和明确错误；RPC 与 rdbcomm 服务端接入该入口。

## Seam 分析

### 声明的测试接缝

- seam: `libs/tests/rpc_handshake_test.c` -> `libs/rpc-handshake.c`
- seam: `rpc/tests/rpc_tool_integration.cpp` -> `rpc/rpc-server.cpp`, `libs/rpc-handshake.c`
- seam: `rdbcomm/tests/tool_integration.c` -> `rdbcomm/server.c`, `libs/rpc-handshake.c`

## 验收标准

- [ ] AC-1: 执行握手单元测试，服务端首阶段分别验证 TIME 后关闭、明文协商成功、客户端请求 mTLS 协商成功、算法不匹配明确失败。
- [ ] AC-2: 执行服务端强制 mTLS 测试，客户端未请求 mTLS 或算法不匹配时被拒绝，不能降级明文；有效算法证书链缺失时服务初始化失败。
- [ ] AC-3: 执行服务端非强制 mTLS 测试，无证书时明文仍可用；有证书时客户端可主动请求 mTLS；mTLS 证书不可用时明确失败且不降级。
- [ ] AC-4: 执行真实 RPC 与 rdbcomm 工具集成测试，明文和 mTLS 均能进入各自第二阶段；mTLS 第二阶段通过 TLS session 读写。
- [ ] AC-5: 执行 `xmake build` 和 `xmake test`，构建成功且所有测试通过；RPC/rdbcomm 不再保留重复的服务端首阶段编排。
- [ ] AC-6: 执行客户端/服务端配置参数覆盖测试；RPC/rdbcomm 客户端和服务端均通过显式握手配置结构传递 mTLS 开关与算法，不新增 CLI 参数、不改变协议字段、不改变 ca_cn 证书选择逻辑。
- [ ] AC-7: 执行 `git diff --check` 和引用扫描，结果通过；公共握手入口无重复编排，客户端与服务端参数语义一致。

## 方案与取舍

- 公共入口通过配置结构体传递客户端 `mtls_enabled`、算法，以及服务端 `mtls_required`、算法和 `ca_cn`，不使用回调。
- 服务端未启用 mTLS 时允许明文；客户端主动请求且算法匹配时允许 mTLS。
- 服务端启用 mTLS 时将 mTLS 作为硬要求，协商失败直接返回错误并关闭；有效算法对应证书链缺失时启动失败。
- 服务端未启用 mTLS 时允许明文；证书链存在则支持客户端主动 mTLS，证书链不存在则仅提供明文并对 mTLS 请求报错。
- 未配置具体算法时默认 `RPC_HS_ALG_CLASSIC`（AES/普通证书路径）；配置了具体算法则校验对应证书链。
- `TIME` 是终止操作，只返回时间，不进入第二阶段。
- 保留 `tls_cert` 的证书和 OpenSSL 细节，握手模块只负责统一编排和 session 绑定。

## 范围外

- 不新增 CLI 参数，不兼容旧协议，不修改协议字段。
- 不修改客户端证书按 `ca_cn` 目录选择的既有逻辑。
- 不改变 RPC/rdbcomm 第二阶段业务帧格式。
- 不新增命令行参数；工具仅把各自既有配置转换为握手配置结构体。

## 参数接口

- `rpc_hs_client_config_t`：客户端显式传递 `mtls_enabled` 与算法。
- `rpc_hs_server_config_t`：服务端显式传递 `mtls_required`、算法与 `ca_cn`。
- RPC/rdbcomm 的工具配置入口保持独立，握手层不读取全局配置。

## Seam 分析

### 声明的测试接缝
- seam: `libs/tests/rpc_handshake_test.c` -> `libs/rpc-handshake.c`
- seam: `rpc/tests/*` -> `rpc/rpc-io.cpp`、`libs/rpc-handshake.c`
- seam: `rdbcomm/tests/tool_integration.c` -> `rdbcomm/client.c`、`rdbcomm/server.c`
- seam: `libs/tests/xmake.lua` -> `xmake build`、`xmake test`
