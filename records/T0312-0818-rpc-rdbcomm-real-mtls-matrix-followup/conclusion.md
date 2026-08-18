---
schema: pdca.asset/v1
id: T0312-0818-rpc-rdbcomm-real-mtls-matrix-followup
phase: check
source_ids: [xmake-full, implementation-diff, rpc-time-test, rdbcomm-mtls-test]
---

## 上下文

本轮针对 RPC/rdbcomm 工具层补充独立 `time` 子命令、真实进程测试、tls-keygen 证书生成和 mTLS 失败矩阵；不新增客户端参数。

## 假设与结果

- AC-1：通过。测试由 tls-keygen 生成 CA、服务端证书及两个客户端证书，并按服务端返回的 `ca_cn` 建立客户端证书目录。
- AC-2：部分通过。明文和 classic mTLS 的 RPC/rdbcomm 应用帧测试通过；SM2 真实 rdbcomm 应用帧仍在握手后连接失败，现有 TLS 单元测试的 SM2 握手通过，但不足以证明工具应用数据面通过。
- AC-3：通过。覆盖算法不匹配、客户端证书缺失、服务端启用 mTLS 时客户端明文连接，均以客户端失败/连接关闭结束；日志显示没有降级为成功应用会话。
- AC-4：通过。RPC 与 rdbcomm 均使用独立 `time` 子命令；时间请求不初始化客户端证书，不进入第二阶段应用帧。
- AC-5：通过。新增测试目标注册到 `xmake test`，全量 36/36 通过，未增加客户端参数。

## 分析

独立 TIME 路径已经与应用命令参数分离，且客户端在 TIME-only 之前不要求证书，因此算法或证书异常不会阻断时间查询。经典 mTLS 应用数据沿 `rpc_hs_session_t` 的 TLS 读写路径运行。SM2 失败点发生在真实 rdbcomm 工具握手后的连接阶段，当前证据不能支持把 SM2 应用数据面标记为完成；需要下一轮增加 TLS 错误细节和逐步比对 RPC/rdbcomm 的 SM2 session 初始化。

## 失败原因（partial）

现有 SM2 证书初始化成功，但 rdbcomm 客户端应用连接返回失败，服务端日志仅显示 TLS handshake failed，缺少可定位的 OpenSSL 错误栈。因此 AC-2 的 SM2 子场景尚未闭环。

## 适用边界

本结论覆盖当前 Linux debug 构建、真实 `rdbcommd/rdbcomm` 与 `aio-speedd/aio-speed` 工具进程及现有环境配置；不代表 SM2 应用帧在所有部署证书链/算法组合下均可用。

## 下一轮建议

创建跟进任务定位并修复 SM2 rdbcomm 工具应用帧失败，补充服务端/客户端 OpenSSL 错误码断言，并在 RPC 与 rdbcomm 两个工具上完成 SM2 应用帧双向往返后再重新判定 AC-2。

## Verdict

outcome: partial
verdict_id: T0312-check-20260818-partial
reason: AC-1、AC-3、AC-4、AC-5 已有证据；AC-2 的 SM2 真实应用数据面未闭环。
at: 2026-08-18T15:11:00+08:00
