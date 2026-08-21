# T0336 — tls_cert_ssl_free：封装 SSL 释放 API

## 背景
`tls_cert_handshake_common`（libs/tls_cert.c:337）通过 `SSL_new` 创建 SSL 对象并返回给调用方。当前调用方需自行调用 `SSL_shutdown` + `SSL_free` 释放 SSL（rpc-io.cpp:72-73、tls_cert_test.c 多处）。tls_cert 模块创建 SSL 但不提供释放 API，违反封装原则，且调用方容易遗漏 `SSL_shutdown`。

## 需求
1. 新增 `void tls_cert_ssl_free(SSL *ssl)` API（libs/tls_cert.c/.h）
   - 内部调用 `SSL_shutdown(ssl)` + `SSL_free(ssl)`
   - ssl 为 NULL 时安全返回
2. 替换所有生产代码中 `SSL_shutdown + SSL_free` 为 `tls_cert_ssl_free`
   - rpc/rpc-io.cpp:72-73（rpc_io_cleanup）
   - libs/tests/tls_cert_test.c 全部 SSL_shutdown+SSL_free 调用点
3. `xmake build` + `xmake test` 全部通过

## 验收标准
- [ ] AC-1: `tls_cert_ssl_free` 声明在 libs/tls_cert.h，实现在 libs/tls_cert.c
- [ ] AC-2: 所有生产代码 SSL 释放改用 `tls_cert_ssl_free`（grep `SSL_free` 仅剩 tls_cert.c 内部和外部库）
- [ ] AC-3: `xmake build` 通过
- [ ] AC-4: `xmake test` 38/38 通过（含 tls_cert_test）

## 范围外
- 外部库（libtimed_net_key.so）的 SSL 释放不在此任务范围
- SSL_CTX 生命周期不变（仍由 tls_cert_cleanup 管理）
