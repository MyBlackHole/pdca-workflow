---
schema: pdca.asset/v1
id: T0366-0823-tls-cert-p2-followup
phase: check
source_ids: [ev-tls-cert-p2-tests]
---

## 上下文
T0365 已完成 TLS 证书子系统四类缺陷修复（双向身份绑定 / ciphersuites fail-closed / ca_cn 确定性 / 客户端 ctx 缓存并发复用）。本任务 T0366 是其 P2 安全增强，补齐四项长期能力缺口：证书热加载/轮换（AC-1）、CRL 吊销检查（AC-2）、错误码前缀归一（AC-3）、审计记录真实对端 CN（AC-4）。实现位于 AIO 仓库 `libs/tls_cert.c` / `libs/tls_cert.h`，验证位于 `libs/tests/tls_cert_test.c`（新增 4 个用例）。

## 假设与结果
- 假设 H1：可在不改动调用约定的前提下为 ctx 增加 reload 入口，且 reload 不中断在途握手。→ 成立（AC-1 通过）。
- 假设 H2：OpenSSL 4.0.1 的 `X509_V_FLAG_CRL_CHECK|X509_V_FLAG_CRL_CHECK_ALL` 可在握手验证阶段拒绝被吊销证书，且为 fail-closed。→ 成立（AC-2 真实拒绝原因 `verify_result=23 certificate revoked`）。
- 假设 H3：错误码已统一为 `TLS_CERT_ERR_*` 负值，无需大规模重构。→ 成立（AC-3 通过，文件缺失返回对应负值）。
- 假设 H4：握手后可在 `TLS_SSL` 记录对端 subject CN 供审计使用。→ 成立（AC-4 通过，`tls_cert_get_peer_cn` 返回服务端证书 CN=black）。

## 分析
- AC-1：新增 `tls_cert_slot_reload` + `tls_cert_ctx_reload(ctx,algorithm)` + `tls_cert_client_ctx_reload(cert_dir,algorithm,ca_cn)`，挂载点兼容既有客户端 ctx 缓存（T0365）；reload 持 `tls_cert_ccache_lock` 重建底层 `SSL_CTX`，旧 ctx 因在途 `SSL` 引用计数延迟释放，避免并发 UAF。
- AC-2：仅实现 CRL（本地 crl.pem）检查；OCSP 按 PRD 列为偏离项——CRL 已满足“被吊销证书拒绝”硬验收，OCSP stapling 缓存作为后续增强（disposition 记录）。
- AC-3：错误码前缀 `TLS_CERT_ERR_*`、负值返回，fail-closed 范式沿用 T0358。
- AC-4：`TLS_SSL.peer_cn` 在 `handshake_common` 提取对端 subject CN，客户端/服务端双角色审计均记真实对端 CN。

## 适用边界
- 证书热加载仅覆盖文件被替换/损坏场景；监听 reload 触发（信号/inotify）由上层调用点负责，本任务未实现自动触发。
- CRL 为本地文件，无在线 OCSP/CRL 分发与刷新周期；吊销时效性依赖 crl.pem 更新频率。
- 测试需从 `libs/` 目录运行（相对 cert 路径）；负向握手用例依赖 `signal(SIGPIPE, SIG_IGN)` 防止进程被杀。

## 下一轮建议
- AC-2 后续：OCSP stapling 服务端缓存（PRD 范围外）。
- reload 自动触发：inotify/信号监听封装。
- 知识沉淀：将“reload 重建 SSL_CTX 须把 `app_data` 重定向到长生命周期 slot->ca_cn（避免 verify 回调悬空指针）”记入 `knowledge/tls/`。
