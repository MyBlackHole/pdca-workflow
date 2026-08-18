---
schema: pdca.asset/v1
id: T0309-0818-mtls-implementation-review
phase: check
source_ids: [review-report, verification-snapshot]
---

## 上下文

本次审查以 `df6b6145^..HEAD` 为代码基点，核对用户确认的 rpc/rdbcomm 首阶段协议约束，并映射 `/home/black/Public/aio/F/139/备份传输存储加密/备份复制传输加密.md` 中适用于 RPC/rdbcomm 的要求。

## 假设与结果

结论为 `partial`：统一握手、时间获取、服务端强制 mTLS、rdbcomm 主数据面和部分 RPC session 数据面成立；RPC 全量业务 mTLS 不成立。最高风险是 fd-only RPC 连接接口在 mTLS 协商成功后主动失败，且大量业务路径仍使用 fd-only I/O。

逐项验收判定：

- AC-1：满足。报告覆盖 RPC、rdbcomm、tls_cert、配置和测试。
- AC-2：满足。报告核对时间、mTLS 应用帧和未知帧三场景；未知帧错误精度另列风险。
- AC-3：部分满足。协议决策一致，但 RPC fd-only 路径导致全业务 mTLS 不成立。
- AC-4：部分满足。握手结构体读写指针和 TLS I/O 已核对；服务端 SSL cleanup、超时和 SSL 错误映射存在缺口。
- AC-5：部分满足。ca_cn 传递和客户端按目录选择已核对；算法仅按 SM/classic 二值化，具体协商套件可观测性不足。
- AC-6：满足（范围映射）。RPC/rdbcomm 相关基线已映射，SBT/UI/存储加密等范围外差距已单列。
- AC-7：满足。已给出 P0/P1/P2 优先级、影响、最小方向和验证方式。
- AC-8：满足。构建、测试、静态检查和 clean worktree 证据已登记，未引入实现代码改动。

## 分析

验证命令全部通过，但测试证明范围有限：TLS 单测证明 TLS/SM2 数据收发，RPC 应用测试证明明文首阶段后的应用帧；没有证明真实 RPC/rdbcomm 进程在首阶段协商 mTLS 后完成业务数据帧。因此“测试全绿”不能推导“RPC 全量 mTLS 已完成”。

## 失败原因（仅 rejected/partial）

1. RPC 同时保留 session I/O 与 fd-only I/O 两套连接模型，连接 API 的返回类型无法携带 SSL 所有权。
2. 服务端普通 worker 退出路径没有统一释放 `woker_info->io.ssl`。
3. 握手解析/响应校验和错误映射不够严格，且握手/时间请求缺少明确 deadline。
4. 现有测试未覆盖真实 RPC/rdbcomm 的 mTLS 应用业务帧。

## 适用边界

本结论仅覆盖本次最近代码及 RPC/rdbcomm 相关基线映射，不代表 SBT、UI、作业层配置、完整国密后端、存储加密或性能容量目标已满足。

## 下一轮建议

优先创建/执行后续修复任务：

1. RPC 连接和业务函数全面 session 化，消除 fd-only mTLS 失败路径。
2. 补唯一 cleanup、SSL 错误映射、握手/时间超时和严格 operation/version 校验。
3. 增加真实 RPC/rdbcomm 进程的明文、mTLS、SM2、失败不降级和时间功能矩阵测试。
4. 修复后重新执行本审查的 AC-3/AC-4/AC-5。

## Verdict

- verdict_id: V-T0309-partial
- outcome: partial
- reason: 基础协议与部分密文路径成立，但 RPC 全量 mTLS 存在已证实的 fd-only 连接缺陷，需后续修复和真实业务回归。
- at: 2026-08-18T14:12:12+08:00
