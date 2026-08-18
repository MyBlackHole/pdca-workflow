---
schema: pdca.asset/v1
id: T0302-0818-rdbcomm-rpc-mtls-time
phase: check
source_ids: [build-test-tls-v2, tls-session-test-v2, real-process-test, handshake-impl, rdbcomm-adapter, rpc-server-adapter, design-session, prd-decisions]
---

## 上下文

已完成统一第一阶段握手、TIME 分支、RPC/rdbcomm 会话接入，以及基于会话读写指针的 TLS 密文数据面测试。

## 假设与结果

- AC-1：通过。统一固定头编解码和字段断言通过。
- AC-2：通过。RPC 与 rdbcomm 真实服务进程均返回统一 TIME 响应并关闭连接。
- AC-3：通过。RPC 与 rdbcomm 真实服务进程均返回 OK_PLAIN。
- AC-4：通过。两套真实服务均完成 NEGOTIATE 后 TLS 升级，并通过 TLS socket 收发 APP 探针。
- AC-5：通过。两套真实服务均返回 `ca_cn=Real Test CA`，客户端从 `cert_dir/Real Test CA/` 选择证书并完成 TLS。
- AC-6：通过。真实 mTLS 连接使用 TLS 1.3 加密套件，组件回环同时证明会话读写指针和 SSL 生命周期。
- AC-7：部分通过。真实服务已覆盖坏 magic、半包关闭、算法不匹配和强制 mTLS 不请求，均明确失败且无降级；缺证书和等待超时的完整服务断言仍待补充。
- AC-8：通过。真实服务未知 operation 返回 0x8003 并关闭；旧客户端兼容不在范围内。
- AC-9：通过。真实 rdbcomm 服务进程返回与 RPC 相同格式的 TIME 响应。
- AC-10：部分通过。`rpc_get_time` 已切换统一协议并构建通过，完整旧调用回归尚未执行。
- AC-11：部分通过。默认明文、显式 mTLS 和异常协商的两套真实服务测试通过，完整业务回归尚未执行。
- AC-12：通过基础配置验证。真实服务使用配置的 `RPC_TLS_CA_CN` 返回并完成对应目录证书选择；多算法矩阵仍未执行。

## 分析

新增 TLS 会话回环测试和真实 RPC/rdbcomm 服务进程测试。两套服务均证明 TIME、默认明文、未知 operation、服务端返回 `ca_cn`、客户端证书目录选择和 TLS 加密升级路径可工作。

## 适用边界

当前结论适用于协议编解码、TIME、默认明文、基础 mTLS 配置、证书目录选择和 TLS 会话生命周期；仍不覆盖完整业务回归、多算法矩阵、超时和缺证书服务进程场景。

## 下一轮建议

下一轮补充真实服务进程的超时和缺证书测试，并执行完整业务回归与多算法矩阵。

## Verdict

- outcome: partial
- verdict_id: T0302-check-20260818-01
- reason: 真实服务进程的核心协议、基础 mTLS 和主要协商错误场景已通过；缺证书/等待超时断言及完整业务回归仍缺失，旧版兼容不在范围内。
- at: 2026-08-18T13:34:00+08:00
