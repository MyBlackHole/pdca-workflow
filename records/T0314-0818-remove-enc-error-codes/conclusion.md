---
schema: pdca.asset/v1
id: T0314-0818-remove-enc-error-codes
phase: check
source_ids: [xmake-full, enc-scan, tls-logs, tls-test, implementation-diff]
---

## 上下文

本任务审查并优化最近的 mTLS 实现：移除项目自定义 `ENC-*` 错误编码，并补充可直接定位问题的 TLS 日志。第三方 OpenSSL 中的 `ENC-then-MAC` 文本不在范围内。

## 假设与结果

- AC-1：通过。项目源码范围内扫描不到自定义 `ENC-*` 引用；扫描结果见 `enc-scan`。
- AC-2：通过。SM2 证书链加载失败日志包含阶段、CA/证书/私钥路径；配置失败日志补充角色和算法；握手失败日志包含角色、阶段、算法、SSL 错误及 OpenSSL 错误队列；服务端证书校验失败日志包含校验结果和客户端 CN。实现见 `tls-logs`，真实失败输出见 `xmake-full`。
- AC-3：通过。`xmake test -v` 通过 36/36；真实 RPC、rdbcomm、SM2 mTLS、证书缺失和不降级场景均通过。原有返回码、失败即停止和禁止明文降级逻辑未改变，见 `xmake-full` 与 `implementation-diff`。

## 分析

本次修改只改变诊断信息和调用上下文，不改变协议、CLI 参数、返回码或 TLS 降级策略。SM2 证书链加载函数保留原有失败边界；由 client/server 初始化调用点传入角色，使错误日志能够区分服务端和客户端。

## 适用边界

日志中的算法来源于当前 TLS 配置；OpenSSL 在握手失败时没有错误队列的情况仍会记录 `ssl_error`。私钥内容不会写入日志，仅记录路径。旧的第三方 OpenSSL `ENC-then-MAC` 文本仍然存在，这是明确排除项。

## 下一轮建议

若后续需要统一所有 rdbcomm 上层握手错误日志，可再将 `rdbcomm/server.c` 的通用失败日志接入同一结构化字段；本任务不扩大范围，因为 TLS 层已输出具体原因且完整真实工具测试已覆盖。

## Verdict

- proposed outcome: confirmed
- reason: 三项验收标准均有注册证据支持，完整测试通过，未发现行为回归。
