---
schema: pdca.asset/v1
id: T0365-0823-tls-cert-processing-hardening
phase: check
source_ids: [tls-cert-test-all, full-build, ac4-tsan, convergence-map-2]
---

## 上下文

T0365 针对四模块（rdbcomm / dmsbtex / libobk / rpc）共用的证书处理中枢
`libs/tls_cert.c`，修复四类安全纵深/确定性缺陷（AC-1~AC-4）。四模块经统一
`tls_cert_*` 接口间接受益，未逐模块改动。Do 阶段已完成源码改造与单测，研发阶段
经 Grill 暴露 AC-4 并发证据缺口后，补做多线程并发压测与 TSan 验证。

## 假设与结果

- **H1（AC-1 双向身份绑定）**：对端身份可由 `SSL_set_verify` 回调校验
  `issuer CN == 协商 ca_cn` 实现 pin。结果：`tls_cert_verify_peer_cn` 回调落地，
  `slot->ca_cn` 服务端/客户端双向填充；单测"链有效但 CN 不匹配"握手被拒绝（PASSED）。
- **H2（AC-2 ciphersuites fail-closed）**：套件设置失败应返回错误而非静默降级。
  结果：`tls_cert_set_ciphersuites` 改 `int` 返回，调用点检查并 cleanup+报错；单测
  注入非法算法名 `init` 失败（PASSED）。
- **H3（AC-3 ca_cn 确定性）**：可确定性从主 CA 文件首证书解析 subject CN。
  结果：`tls_cert_ca_cn_from_file` 读取首证书 CN，替换 `X509_STORE_get1_objects`
  遍历；单测多 CA 对象下稳定等于主 CA CN（PASSED）。
- **H4（AC-4 客户端 ctx 缓存复用 + 并发安全）**：可按
  `(cert_dir, algorithm, ca_cn)` 键控复用同一 SSL_CTX 且并发安全。结果：
  `acquire/release` + 全局 `pthread_mutex` + 引用计数；单测复用同一 ctx；
  并发压测（8 线程×300 + 主线程×800 次 acquire→SSL_new→SSL_free→release）
  无崩溃；**TSan 零数据竞争报告**。

## 分析

- **AC-1（confirmed）**：fail-closed，链验证失败或 issuer CN 不匹配一律拒绝。
  证据 `tls-cert-test-all`（`tls_cert_peer_identity_binding_reject` PASSED）。
- **AC-2（confirmed）**：fail-closed，套件设置失败返回错误不降级。
  证据 `tls-cert-test-all`（`tls_cert_set_ciphersuites_fail_closed` PASSED）。
- **AC-3（confirmed）**：确定性，取主 CA 文件首证书 CN，与 X509_STORE 遍历顺序无关。
  证据 `tls-cert-test-all`（`tls_cert_ca_cn_from_file_deterministic` PASSED）。
- **AC-4（confirmed）**：并发安全（硬约束）。全局表加锁保护；引用计数归零才
  `tls_cert_cleanup`；OpenSSL `SSL_CTX` 引用计数兜底。多线程高压用例无崩溃/无双重
  释放，TSan 检测零竞争。证据 `tls-cert-test-all` + `ac4-tsan`。
- **全量构建**：4 个调用方（dmsbtex/network.c、rpc/rpc-io.cpp、libobk/lib/sbt/
  libobk.c、rdbcomm/client.c）改为 acquire/release 后编译通过。证据 `full-build`。
- **收敛链**：`validate-convergence.py` 返回 `valid: true`，无 issue。

## 失败原因

无（预期 verdict = confirmed）。

## 适用边界

- ED25519 隐式回退为兼容旧证书刻意保留，本次不去除。
- 缓存并发安全依赖调用契约：每个 `acquire` 须配对一个 `release`，且 `release`
  后不得再访问该 `ctx`。当前四个调用方均遵循。

## 下一轮建议

- P2 跟进：证书热加载/轮换、CRL/OCSP 吊销检查、错误码前缀归一（T0364 follow-up）、
  审计对端 CN（P2-5，顺带）。
- 将 `tls_cert_test` 接入 CI 的 ASan/TSan 门禁，固化并发安全证据（本次为临时注入
  TSan 验证，已还原构建配置）。

## 逐条 AC 判定

- AC-1：confirmed — 双向身份绑定回调已落地，拒绝用例 PASSED。
- AC-2：confirmed — ciphersuites fail-closed，失败返回错误，init 失败用例 PASSED。
- AC-3：confirmed — ca_cn 确定性解析，单测稳定 PASSED。
- AC-4：confirmed — 客户端 ctx 缓存复用 + 并发安全（多线程压测 + TSan 零竞争）PASSED。

## Verdict

- verdict_id: T0365-CHECK-001
- outcome: confirmed
- reason: 四项 AC 均有针对性单元测试与全量构建证据支撑；AC-4 并发硬约束补做
  多线程压测并通过 TSan 零竞争验证；收敛链校验 valid:true。
- at: 2026-08-23T08:04:00+08:00
