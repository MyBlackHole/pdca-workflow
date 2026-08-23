# Do 阶段证据 — T0365（TLS 证书处理流程安全纵深与确定性优化）

## 实现产物
- `libs/tls_cert.c` / `libs/tls_cert.h`（AC-1~AC-4 核心）
  - **AC-1 双向身份绑定**：新增 `tls_cert_verify_peer_cn` 校验回调，链验证通过后比对
    对端证书 issuer CN == 协商 `ca_cn`（即从主 CA 文件解析的 subject CN），不匹配即
    fail-closed 拒绝；`slot->ca_cn` 原仅在服务端分支填充，已改为服务端/客户端双向通用填充。
  - **AC-2 ciphersuites fail-closed**：`tls_cert_set_ciphersuites` 由 `void` 改 `int`，
    套件名无效或设置失败返回 `TLS_CERT_ERR_INVALID_PARAM`/`TLS_CERT_ERR_SSL_CREATE`，
    `slot_create` 调用点检查返回并 cleanup+报错，不再静默降级。
  - **AC-3 ca_cn 确定性解析**：新增 `tls_cert_ca_cn_from_file`，从主 CA 证书文件读取
    **首证书** subject CN（不依赖 X509_STORE 遍历顺序）；服务端 `slot_create` 改用之
    替换原 `X509_STORE_get1_objects` 遍历取首个的写法。
  - **AC-4 客户端 ctx 缓存复用（并发安全）**：新增 `tls_cert_client_ctx_acquire` /
    `tls_cert_client_ctx_release`，按 `(cert_dir, algorithm, ca_cn)` 键控复用同一 ctx，
    全局表由独立 `pthread_mutex` 保护，引用计数归零才真正 `tls_cert_cleanup`；
    SSL_CTX 线程安全，多连接/线程共享同一 ctx 无 UAF。
- `libs/tests/tls_cert_test.c`：新增 AC-1 拒绝、AC-2 fail-closed、AC-3 确定性、AC-4 复用 测试。
- 4 个调用方改造为 acquire/release（消除每次连接重复读证书与构建 SSL_CTX）：
  - `dmsbtex/network.c:182`
  - `rpc/rpc-io.cpp:153`
  - `libobk/lib/sbt/libobk.c:195`
  - `rdbcomm/client.c:201`

## 验证结果
- 单元测试：`cd libs/tests && xmake run tls_cert_test` → **12/12 PASSED**
  （含现有 `tls_mtls_handshake` 等 mTLS 回归用例，确认合法握手仍正常）
- 全量构建：`cd <repo> && xmake build` → **build ok**（含上述 4 调用方模块编译通过）

## 代码审查要点（A4）
- **并发安全**：缓存表读写与 refcount 变更均在 `pthread_mutex` 临界区内；同一 ctx 被多个
  连接/线程共享时，仅最后一个 `release`（refcount 归零）才 cleanup，期间其他线程持有的
  SSL* 由 OpenSSL 引用计数保障存活，无双重释放/UAF。
- **fail-closed**：AC-1 链验证失败或 issuer CN 不匹配一律拒绝；AC-2 套件设置失败直接拒绝
  该 profile（返回错误，不静默 OK）。
- **无降级**：mTLS 握手失败时调用方均走 error 分支断开，不回退明文。
- **确定性**：AC-3 取文件首证书 CN，与 X509_STORE 内部遍历顺序无关，多 CA 文件下稳定。
- **ED25519 隐式回退保留**：按用户决策为兼容旧证书未去除（AC-4 原"ED25519 移除"项已撤销）。
