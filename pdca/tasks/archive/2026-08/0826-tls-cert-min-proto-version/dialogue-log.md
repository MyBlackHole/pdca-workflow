# Dialogue Log — T0391（Plan → Do）

## Plan 阶段
- 来源：T0388/T0389/T0390 后"mTLS 全面深度审查"发现 F1（中危）。
- 问题：libs/tls_cert.c 生产 TLS 上下文 `SSL_CTX_new(TLS.method())` 未显式设最低协议版本，仅依赖 OpenSSL 默认与 TLS1.3 套件隐式约束。
- 决策（P6 终审 confirmed）：显式设 `TLS1_3_VERSION`；仅新增一行下限设置，不改动套件/算法/验证回调。
- 查重：无重复任务（命中 0823-oss-https-cert 为 Go OSS 证书任务，无关）。

## Do 阶段（bugfix 路径 B）
- B1 根因：同上，确认 tls_cert.c:236 后无 `SSL_CTX_set_min_proto_version`。
- B2 修复：tls_cert.c `tls_cert_slot_create` 中 `SSL_CTX_new` 成功后新增
  `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`，失败 fail-closed（free+return）。
  该函数在 server/client 上下文创建共用，一处覆盖全部生产上下文。
- B2 回归测试：libs/tests/tls_cert_test.c 新增 `tls_cert_min_proto_version_enforced`，
  经由既有 `tls_cert_get_ssl_ctx` 取 SSL_CTX 并断言 `SSL_CTX_get_min_proto_version == TLS1_3_VERSION`
  （AES + SM4 两个 slot）。可判别：无修复时 OpenSSL4 默认最低 TLS1.2，断言必失败。
- B3 验证：`xmake build tls_cert_test` 通过；运行 20 个用例全 PASSED（含新增用例，原有用例无回归）。
- 证据：build-log / test-log / diff-log 已登记（带 digest），convergence-map 校验 valid:true。
- B4 代码审查（简版）：改动最小、fail-closed、TLS1_3_VERSION 头文件已在用、双 slot 均覆盖、无回归。
- 代码提交：按全局规则暂缓，待用户显式"提交"指令（沿用 T0388/T0389/T0390 惯例）。
