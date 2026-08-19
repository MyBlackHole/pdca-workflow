---
schema: pdca.asset/v1
id: T0310-0818-mtls-rpc-session-followup
phase: check
source_ids: [validation-summary, implementation-review]
---

## 上下文

本轮针对 T0309 暴露的 RPC fd-only 数据面问题，执行了 session-only 迁移、握手严格校验、清理路径修复，并将 RPC/rdbcomm 工具目标加入 xmake 测试注册。

## 假设与结果

- AC-1：部分支持。RPC 主要业务入口已显式使用 `rpc_io_t`；仍保留底层 fd helper 声明，尚未完成全仓库接口收缩。
- AC-2：部分支持。RPC worker、rdbcomm 客户端失败路径补充了 SSL cleanup；尚未完成所有异常注入场景证明。
- AC-3：部分支持。握手响应 operation 校验已有红绿回归测试，错误帧转发和已有 socket timeout 路径已验证；尚未补齐独立 timeout 断言矩阵。
- AC-4：未完成。尚未覆盖真实 RPC/rdbcomm 进程的常规 mTLS、SM2、算法不匹配、缺证书和强制 mTLS 不降级矩阵。
- AC-5：部分支持。`rpc_tool_integration`、`rdbcomm_tool_integration` 已注册 `add_tests("default")` 并通过定向 `xmake test`；rdbcomm 已执行真实明文 server/client 命令往返，RPC 工具目前只验证真实二进制启动入口，时间获取和真实 mTLS 业务往返尚未接入。

## 分析

代码编译通过；握手、目录树、下载链接及两个工具目标的定向 xmake test 均通过。现阶段最主要的缺口不是 session 迁移编译问题，而是测试 fixture 与工具配置的真实证书目录/CA-CN 选择链，以及缺少可从工具命令触发的时间获取场景。

## 失败原因（仅 rejected/partial）

真实工具 mTLS 测试需要按服务端返回的 `ca_cn` 建立证书目录，并同时覆盖客户端多证书选择；当前 `libs/tests/certs` fixture 与运行时 CA-CN 目录选择不一致，不能据此宣称 mTLS 业务测试通过。RPC 工具现有命令行也没有在本轮新增时间参数的授权范围内提供独立 time 子命令。

## 适用边界

本轮结果可作为 session-only RPC 业务迁移和握手校验的中间基线，不可作为完整 mTLS 交付验收结论。

## 下一轮建议

建立 tls-keygen 生成的、按 `ca_cn` 分目录的独立测试 fixture；增加不改变生产客户端参数的测试专用进程编排，覆盖 time-only、mTLS app frame、算法/证书失败和强制 mTLS；随后补齐 RPC 工具的真实业务往返并重新 Check。

## Verdict

outcome: partial
verdict_id: T0310-check-partial-20260818
reason: session-only 迁移与基础回归已完成，但完整真实工具 mTLS/时间/算法矩阵未完成。
at: 2026-08-18T14:45:00+08:00
