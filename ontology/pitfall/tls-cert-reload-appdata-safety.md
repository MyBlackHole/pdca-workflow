---
schema: pdca.asset/v1
id: ontology:pitfall/tls-cert-reload-appdata-safety
type: pitfall
layer: Knowledge
status: active
summary: TLS 证书 ctx 热加载的安全陷阱
source_task: T0366
relations:
  specializes: [ontology:pitfall]
  guides: [ontology:entity/x509-certificate]
attributes:
  - name: applicability
    desc: 持有长生命周期 SSL_CTX 缓存槽的证书热加载/轮换
    constraint: ""
    testable_signal: reload 后 app_data 重定向到长生命周期槽，避免 UAF；测试忽略 SIGPIPE
---

# TLS 证书 ctx 热加载的安全陷阱
# TLS 证书 ctx 热加载的安全陷阱

## 适用场景
在持有长生命周期 `SSL_CTX` 缓存槽（如 `tls_cert_slot`）的 TLS 封装中，实现证书热加载/轮换（重建底层 `SSL_CTX`）。

## 陷阱 1：verify 回调 app_data 指向局部变量（use-after-free）
`tls_cert_slot_create` 内部常用 `SSL_CTX_set_app_data(ctx, (void *)slot->ca_cn)` 把校验回调需要的 CA CN 挂到 ctx 上。`slot->ca_cn` 是 `slot` 的成员，长生命周期时安全。

但在 **reload** 路径里，若先用局部 `tls_cert_slot tmp` 调 `tls_cert_slot_create` 重建 `SSL_CTX`，则新 ctx 的 `app_data` 指向 **`tmp.ca_cn`（栈上局部数组）**。reload 返回后 `tmp` 释放，旧 `app_data` 指针悬空；后续握手时 verify 回调读到垃圾 CA CN → 校验误判（如客户端对服务端证书报 `verify_result=1` 无原因失败）。

**正确做法**：交换底层 `SSL_CTX` 后，必须显式把 `app_data` 重定向到长生命周期槽：
```c
slot->ssl_ctx = tmp.ssl_ctx;
strncpy(slot->ca_cn, tmp.ca_cn, sizeof(slot->ca_cn) - 1);
SSL_CTX_set_app_data(slot->ssl_ctx, (void *)slot->ca_cn); /* 重定向，避免悬空 */
SSL_CTX_free(old_ctx);
```

## 陷阱 2：负向握手用例需忽略 SIGPIPE
任一端拒绝对端证书并关闭连接后，对端 `SSL_accept`/`SSL_write` 会向已关闭 socket 写，触发 `SIGPIPE` 默认终止**整个测试进程**，掩盖真实断言结果。

**正确做法**：测试入口 `signal(SIGPIPE, SIG_IGN)`，交由 OpenSSL 以 `EPIPE` 优雅处理（尤其 AC-2 这类“被拒绝=预期”的负向用例必须如此）。

## 陷阱 3：相对证书路径依赖 CWD
`libs/tls_cert` 测试用 `get_cert_dir()` 返回 `./tests/certs`，相对 **`libs/`** 解析为 `libs/tests/certs`。二进制必须从 `libs/` 目录运行；从仓库根或 `libs/tests/` 运行会因路径错位导致“证书文件缺失”的假失败。

## 调试经验
- OpenSSL 错误码 `0x5800088` = `X509_R_NO_CERTIFICATE_OR_CRL_FOUND`：CA 文件为空或被 `copy_file(src,src)`（以 `wb` 截断自身）破坏。自拷贝同一路径会清空文件。
- `verify_result=23` = `X509_V_ERR_CERT_REVOKED`，是 CRL 吊销检查生效的确证（区别于服务端崩溃导致的 `none received`）。
- 验证 CRL 拒绝时务必加“移除 crl.pem 后握手成功”的正向对照，排除“服务端提前关闭”导致的假绿。
