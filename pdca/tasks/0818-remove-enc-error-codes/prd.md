# 移除 ENC 错误编码并补充明确 TLS 日志

## 问题陈述

当前项目自定义的 `ENC-005` 不能直接说明证书链加载失败的角色、算法和具体文件，排查真实工具失败时信息不足。

## 解决方案

移除自定义 `ENC-*` 文本，统一输出包含 TLS 角色、算法、阶段、CA/证书/私钥路径和 OpenSSL 错误队列的明确日志；保留原有失败返回和禁止明文降级行为。

## Seam 分析

### 声明的测试接缝

- seam: `libs/tests/tls_cert_test.c` -> `libs/tls_cert.c`
- seam: `rdbcomm/tests/tool_integration.c` -> `rdbcomm/rdbcommd`, `rdbcomm`, `libs/tls_cert.c`

## 验收标准


- [ ] AC-1: 在项目源码范围执行 `rg 'ENC-[0-9]+' libs rdbcomm rpc`，结果为 0 个自定义错误编码匹配；第三方 OpenSSL 文本不纳入移除范围。
- [ ] AC-2: 运行 TLS 证书缺失、SM2 链缺失和握手失败测试，日志明确包含角色、阶段、算法及相关证书路径或 OpenSSL 原因。
- [ ] AC-3: 运行 `xmake test`，所有测试通过，且 TLS 初始化失败与禁止明文降级语义不变。

## 范围外

- 不修改 OpenSSL 第三方源码中的 `ENC-then-MAC` 文本。
- 不新增 CLI 参数，不改变协议和函数返回码。
