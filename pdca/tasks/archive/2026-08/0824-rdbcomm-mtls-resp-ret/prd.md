# 【B】rdbcomm mTLS 升级永远失败 — 规格文档

## 问题陈述

- **现状**: `rdbcomm --mtls-enable 1` 握手必败：客户端 TLS 握手期 unexpected eof/SIGPIPE；服务端发 HANDSHAKE_RESP 后直接 close 连接。历史日志 0 次 "upgraded to mTLS"。
- **目标**: rdbcomm/rdbcommd 工具对 mTLS 升级成功，命令执行可用。
- **差距**: 一处返回值误判。

## 根因（strace+gdb 取证）

`send_msg()` 成功时返回发送字节数（如 214），`server.c:528` 对 OK_MTLS 响应用 `!= 0` 判失败 → 成功即 break 关连接。同文件 send_status/send_handle 调用点均正确使用 `< 0`，唯此处误用；单测因 mock 组包绕过真实路径而未拦截。

## 解决方案

server.c:528 `!= 0` 改为 `< 0`；rdbcomm 双场景纳入 T0392 e2e 场景矩阵作回归锚。

## Seam 分析

### 声明的测试接缝
- seam: test/e2e_tool_scenarios.sh -> rdbcomm/server.c

### 验收可测性
- 实机握手 + e2e 脚本断言，独立 pass/fail。

## 用户故事

1. 作为 `运维人员`，我想要 rdbcomm 与 aio-speed 一致的 mTLS 能力，以便各工具统一安全基线。

## 实现决策

- 仅改一处比较运算符；不动 send_msg 语义（其余调用方正确依赖字节数返回）。

## 测试决策

- TDD：先以实机命令复现失败，修复后转绿；回归 handshake_session_test。

## 验收标准

- [ ] AC-1: 实机 `rdbcomm -h 127.0.0.1 -p 6610 -c "echo ok" --mtls-enable 1` 握手成功并输出命令结果
- [ ] AC-2: 明文模式（无 --mtls-enable）rdbcomm 回归正常执行
- [ ] AC-3: rdbcomm/tests handshake_session_test 回归通过
- [ ] AC-4: 该场景写入 T0392 e2e 脚本矩阵并可重复执行

## 范围外

- send_msg 返回值语义重构
- 其他工具对的同类审计（另列）

## 备注

- 发现渠道：T0392 e2e 测试首跑（用户实测先证）。测试基建盲区：mock 绕过真实 send 路径。
