---
schema: pdca.knowledge/v1
title: mTLS 失败日志应同时表达角色、阶段、算法与凭据路径
source: records/T0314-0818-remove-enc-error-codes/conclusion.md
---

## 可复用规则

TLS/mTLS 初始化和握手失败日志应明确记录 `role`、`stage`、实际算法配置，以及 CA、证书和私钥路径；握手失败还应逐条输出 OpenSSL 错误队列。证书校验失败应记录验证结果和对端证书标识，但不记录私钥内容。

错误码只能表达分类，不能替代定位信息。若项目自定义错误编码无法被调用方稳定消费，应移除编码文本，保留原有返回码和失败/禁止降级语义，并通过真实工具测试覆盖证书缺失、算法不匹配和成功握手路径。

## 来源

本条知识由 T0314 的 `libs/tls_cert.c` 诊断改造和 RPC/rdbcomm 真实工具测试验证。
