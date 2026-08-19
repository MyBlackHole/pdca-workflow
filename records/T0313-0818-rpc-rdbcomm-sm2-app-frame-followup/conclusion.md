---
schema: pdca.asset/v1
id: T0313-0818-rpc-rdbcomm-sm2-app-frame-followup
phase: check
source_ids: [xmake-full, implementation-diff, rdbcomm-sm2-test, tls-error-diagnostic]
---

## 上下文

T0312 已确认 classic mTLS 应用帧通过，但 SM2 rdbcomm 应用帧失败。本轮补充失败诊断，并修复真实工具测试的 SM2 `ca_cn` 证书目录接缝。

## 假设与结果

- AC-1：通过。测试使用 `tls-keygen --algo sm2` 生成 CA、服务端和客户端证书；按 `SM2 Test CA` 目录选择客户端证书，真实 rdbcomm SM2 mTLS 应用帧通过。
- AC-2：通过。RPC TIME/classic mTLS 回归通过，rdbcomm SM2 mTLS 应用帧通过，且不使用 `-c time`。
- AC-3：通过。证书缺失、算法不匹配和服务端强制 mTLS 明文降级场景均保持失败并关闭连接；TLS 握手失败会记录 OpenSSL 错误队列。
- AC-4：通过。全量 `xmake test` 36/36 通过，未新增生产 CLI 参数。

## 分析

根因不是 TLS session 的业务读写实现，而是测试传入的证书根目录错误：调用已经包含 `SM2 Test CA` 的目录后，证书选择逻辑再次拼接 `ca_cn`，实际查找路径重复了一层目录。修正测试接缝并改用 tls-keygen 生成的 SM2 链后，现有 session 传输路径可完成应用帧往返。握手失败路径新增 OpenSSL 错误队列记录，便于后续诊断且不改变成功路径。

## 适用边界

结论覆盖当前 Linux debug 构建、OpenSSL 4.0.1 构建依赖、tls-keygen 生成的 SM2 链和真实 rdbcommd/rdbcomm 工具进程；不扩展到 GMSSL/TLCP 后端。

## 下一轮建议

无必须跟进项。保留真实 SM2 工具测试，避免证书根目录与 `ca_cn` 目录重复拼接回归。

## Verdict

outcome: confirmed
verdict_id: T0313-check-20260818-confirmed
reason: 四项验收标准均有真实工具或全量测试证据支持，SM2 应用帧缺口已闭环。
at: 2026-08-18T15:31:00+08:00
