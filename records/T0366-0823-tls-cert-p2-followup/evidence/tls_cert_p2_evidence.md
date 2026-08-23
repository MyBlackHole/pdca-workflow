# T0366 P2 增强 — 验证证据（TLS 证书子系统）

## 构建与运行方式
- 构建（xmake 目标名 `tls_cert_test`）：`cd <repo> && xmake -P . tls_cert_test`
- 运行（必须在 `libs/` 目录下，因 `get_cert_dir()` 返回 `./tests/certs` 相对 `libs/`）：
  `cd <repo>/libs && ./build/linux/x86_64/debug/tls_cert_test`

## 结果
- 退出码：0
- 全部用例：Passed: 17 / Failed: 0
- 新增 4 个 P2 增强用例全部 PASSED：
  - `tls_cert_audit_peer_cn`（AC-4 审计对端 CN）
  - `tls_cert_ctx_reload`（AC-1 证书热加载/轮换 + fail-closed）
  - `tls_cert_error_code_normalized`（AC-3 错误码前缀归一）
  - `tls_cert_crl_revocation_reject`（AC-2 CRL 吊销检查）

## 关键验收点
### AC-2（CRL 吊销，fail-closed）
负向用例：服务端呈现已被吊销证书（RevServer），客户端启用 `crl.pem` 后握手失败。
真实拒绝原因（非服务端崩溃）：
```
TLS client verify failed: verify_result=23 (certificate revoked)
```
正向对照：移除 `crl.pem` 后同一对被吊销证书握手成功（`tssl2 != NULL`），证明拒绝确由 CRL 触发。

### AC-1（证书热加载）
- `tls_cert_ctx_reload(ctx, algorithm)` / `tls_cert_client_ctx_reload(cert_dir, algorithm, ca_cn)` 成功重载底层 SSL_CTX；
- 重载后握手不中断（复用长生命周期 `slot->ca_cn`，修复 reload 期间 verify 回调读到悬空指针的 use-after-free）；
- 损坏证书文件时 `tls_cert_ctx_reload` 返回失败（fail-closed，不污染现有 ctx）。

### AC-4（审计对端 CN）
`TLS_SSL.peer_cn` 在握手后记录真实对端证书 CN；`tls_cert_get_peer_cn()` 返回 `black`（服务端证书 CN），审计日志据此记真实对端 CN（客户端/服务端双角色）。

### AC-3（错误码归一）
新增错误码均以 `TLS_CERT_ERR_` 前缀、负值返回；`tls_cert_init_client/server` 在文件缺失时返回
`TLS_CERT_ERR_LOAD_CA | LOAD_CERT | LOAD_KEY | INVALID_PARAM` 之一（负向用例断言通过）。

## 实现要点（libs/tls_cert.c / tls_cert.h）
- AC-2：仅实现 CRL 检查（X509_V_FLAG_CRL_CHECK|X509_V_FLAG_CRL_CHECK_ALL），OCSP 按 PRD 列为偏离项（CRL 已满足“被吊销证书拒绝”硬验收）。
- 测试入口 `signal(SIGPIPE, SIG_IGN)` 防止负向握手导致进程被 SIGPIPE 杀死（OpenSSL 以 EPIPE 优雅处理）。
