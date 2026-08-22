# client 对 HS_ERR_MTLS_REQUIRED 帧误当业务响应解析的退出码修复 — 规格文档

## 问题陈述

- **现状**: `rpc/rpc-client.cpp:932 execute_shell_script` 等业务函数在 `rpc_recv_io` 后直接按 `msg_cmd_resp_ntoh` 解析，不校验 `uiMT`。当 server 回 `MT_HANDSHAKE_RESP`（如 `HS_ERR_MTLS_REQUIRED`）时被误当业务响应，`uiResult/stat` 字段错位导致 client 可能 exit 0，掩盖拒绝事实。
- **目标**: 业务响应循环内校验 `uiMT != MT_HANDSHAKE_RESP`（或非预期帧类型）即 `error_no=-1` 并断开，使 server 拒绝明文业务时 client 明确失败。
- **差距**: 帧类型校验缺失；AC-5 类场景依赖 server 日志而非 client 语义化失败。

## 解决方案

业务响应消费侧防御：`execute_shell_script` 等 recv 循环内校验帧类型 `uiMT == MT_HANDSHAKE_RESP` 即判定 server 拒绝，`error_no` 记录握手错误码并断开，使 client 语义化失败。测试证书固定使用项目内 `libs/tests/certs`（含 `ca_cn` 目录 `ED25519 Test CA/`），删除 `sm2_client.*` 与旧 RSA `client-001/002` 残留。

## Seam 分析

### 声明的测试接缝

- seam: rpc/tests/mixed_mtls.cpp -> ../rpc-io.h

`mixed_mtls.cpp` 通过真实 aio-speedd/aio-speed 进程覆盖 AC；`../rpc-io.h` 为 client 连接与握手分流入口。
- seam: rpc/tests/mixed_mtls.cpp -> ../rpc-io.h

### 验收可测性

- AC 用真实 aio-speedd/aio-speed 进程验证 client 退出码。

## 用户故事

1. 作为运维，server 强制 mTLS 而客户端未启用时，我希望客户端命令以非 0 退出并输出明确错误，而不是静默成功。

## 实现决策

- **模块**: `rpc/rpc-client.cpp:970` 循环内 recv 后增加：
  `if (ntohl(((msg_base_t*)net_buf)->uiMT) == MT_HANDSHAKE_RESP) { error_no=HS_ERR_MTLS_REQUIRED; ErrorLog(...); break; }`
  同类校验按需覆盖其他业务函数（download/upload 等 recv 点抽查）。
- **技术澄清**: 不改协议帧；仅客户端消费侧防御。

## 测试决策

- 扩展 `mixed_mtls_integration` AC-5：断言 client exit != 0 且 stderr 含 mTLS required。

## 验收标准

- [ ] AC-1: server1 + client0 + `-c true` → client exit != 0。
- [ ] AC-2: client stderr/日志含 "mTLS required" 或等价错误。
- [ ] AC-3: 正常象限（plain/mixed/forced 通）无回归。
- [ ] AC-4: 测试仅使用 `libs/tests/certs` 项目内证书，代码与脚本中无 `/tmp` 证书生成调用（grep keygen/--out 为 0）；`sm2_client.*` 残留已删除。

## 技术澄清（Plan 回补）

- **测试证书约束**：测试必须且只能使用项目内证书资产 `libs/tests/certs`（含 `ca_cn` 目录 `ED25519 Test CA/host.crt+host.key+ca.crt`）；禁止 `/tmp` 自建证书或运行时 keygen 生成。
- **证书残留清理**：删除 `libs/tests/certs/sm2_client.{crt,csr,key}`（违反 T0342 无 client 前缀决议的残留），前置 grep 确认代码零引用。

## 范围外

- 不改握手帧格式；不做自动重试。

## 备注

- T0344 下一轮建议跟进任务。
