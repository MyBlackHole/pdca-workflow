# HS_ERR 帧校验推广至剩余业务 recv 点 — 规格文档

## 问题陈述

- **现状**: T0346 已在 `execute_shell_script`（rpc-client.cpp:961 recv 点）落地帧类型校验；剩余 `:2760`（nc/长命令变体）仍无校验，收到 `MT_HANDSHAKE_RESP` 会被误解析。server 端业务 recv 点（rpc-server.cpp 的 upload 等）为服务端角色，收到的首帧防护已由 handshake_done 分支覆盖。
- **目标**: client 全部 `rpc_recv_io` 响应点具备 `MT_HANDSHAKE_RESP` 帧防御，语义化失败。
- **差距**: 仅剩 1 处 recv 点未覆盖。

## 解决方案

在 `rpc-client.cpp:2760` recv 后复用 T0346 相同模式：校验 `uiMT == MT_HANDSHAKE_RESP` → ErrorLog "server rejected: handshake error result=0x%x" → `error_no = -(int)hs.result` → break。

## Seam 分析

### 声明的测试接缝

- seam: rpc/tests/mixed_mtls.cpp -> ../rpc-io.h

### 验收可测性

- 复用 mixed_mtls_integration 工具级进程验证：拒绝场景 client exit != 0。

## 用户故事

1. 作为运维，任何业务命令在 server 强制 mTLS 拒绝时都应非 0 退出并输出明确错误，无论命令类型。

## 实现决策

- **模块**: 仅 `rpc/rpc-client.cpp:2765` 附近（nc 变体 recv 循环），复制 T0346 校验块。
- **技术澄清**: 不改协议帧；server 端不动。

## 测试决策

- 回归 `mixed_mtls_integration` 全部用例无回归即可（nc 变体走同一 server 拒绝路径）。

## 验收标准

- [ ] AC-1: `rpc-client.cpp` 全部 `rpc_recv_io` 调用点后均有 `MT_HANDSHAKE_RESP` 校验（grep 计数匹配）。
- [ ] AC-2: mixed_mtls_integration 全用例无回归。

## 范围外

- 不改协议帧；不改 server 端。

## 备注

- 来源：T0349 conclusion 下一轮建议。
