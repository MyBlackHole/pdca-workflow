# 客户端 TLS_CTX 缓存复用与并发安全模式

## 问题

四模块（rdbcomm / dmsbtex / libobk / rpc）共用证书中枢 `libs/tls_cert.c`。
服务端已有全局 `server_tls_ctx` / `sbt_server_ctx` 缓存，客户端侧缺失该非对称点：
每次连接都重复读取 CA/cert/key 文件并重建 `SSL_CTX`，握手高频场景下开销显著。

## 模式（AC-4 落地范式）

- **键控**：按 `(cert_dir, algorithm, ca_cn)` 三元组键控，一次 `init` 多次握手复用。
- **存储**：全局固定大小缓存表（`TLS_CERT_CCACHE_MAX`），槽位 `used/key/ctx/refcount`。
- **加锁**：独立 `pthread_mutex` 保护整张表与每个槽的 `refcount`；所有表/refcount
  读写均在临界区内。
- **acquire**：
  - 命中已有键 → `refcount++`，返回同一 `ctx`；
  - 未命中 → `tls_cert_init_client` 建新 `ctx`，`refcount=1`，填入槽。
- **release**：`refcount--`，**仅当 `refcount <= 0`** 才 `tls_cert_cleanup(ctx)` 并清空槽
  （`used=0 / ctx=NULL / key="" / refcount=0`）。

## 并发安全要点

1. 所有缓存表字段与 `refcount` 变更都在 `pthread_mutex` 临界区内，无裸共享写。
2. `tls_cert_cleanup` 仅在 `refcount` 归零时发生——即**所有持有者都已 `release`**，
   此时没有任何线程还在使用 `ctx`，无 use-after-free / 双重释放。
3. 同一 `ctx` 被多连接/线程共享时，底层 `SSL_CTX` 由 OpenSSL 自身的引用计数保障
   存活（`SSL_new` 增引用、`SSL_free` 减引用），即便缓存层 `cleanup` 调
   `SSL_CTX_free`，只要尚有 `SSL*` 存活就不会真正释放。

## 调用契约（适用边界 / 必要前提）

- 每个 `acquire` 必须配对一次 `release`；**`release` 之后不得再访问该 `ctx`**。
- 该契约是并发安全的前提。当前四个调用方均遵循；若未来出现
  "`acquire` 后跨 `release` 仍长期持有 `ctx` 指针" 的误用，将破坏该前提导致 UAF。
- 设计未引入 RCU/epoch 延迟释放机制——刻意保持简单，依赖契约而非运行时 GC。

## 验证方法（推荐固化到 CI）

- 单测：同一键两次 `acquire` 返回同一 `ctx`（`SSL_new(slot->ssl_ctx)` 共享）；
  `refcount` 递增/归零重建验证。
- 并发压测：N 线程（如 8）× 多轮 `acquire → SSL_new → SSL_free → release`，主线程
  同时高频 `acquire/release` 制造 `refcount` 归零重建竞争；验证无崩溃 / 无双重释放。
- **ThreadSanitizer 零竞争**：临时给 `tls_cert` 静态库与测试目标注入
  `-fsanitize=thread`（注意 `add_deps` 的 `tls_cert.c` 也须插桩，否则漏报），运行
  并发压测；期望 **0 个 `WARNING: ThreadSanitizer`**。验证后还原构建配置。

## 关联

- fail-closed 精神（T0358）：链验证失败或 issuer CN 不匹配一律拒绝，不回退明文。
- 双向身份 pin（AC-1）：服务端/客户端均校验对端证书 issuer CN == 协商 `ca_cn`。
- 调用方改造为 `acquire/release` 即自动受益，无需逐模块改动缓存逻辑。
