---
schema: pdca.asset/v1
id: T0344-0822-rpc-mixed-mtls
phase: check
source_ids: ["test-suite-v2", "build"]
---

## 上下文

T0344 目标为 `rpc` 混合/强制矩阵：`server 0` 按 `want_mtls` 双通，`server 1` 强制 `MTLS`。`T0342` 已交付 `cert_dir` 强制与双格式，`libs/` 不动，仅 `rpc` 侧按需分流。

## 假设与结果

- **AC-1** `server 0 want0` 明文无 HS：`PASS` — `test-suite-v2` 中 `plain` 直通 `write/read` 成功，不发 `HS`
- **AC-2** `server 0 want1` 按需密文：`PASS` — `cert_dir` 有建 `sctx`，`want_mtls=1` 回 `MTLS` 且 `tls` 成功
- **AC-3** `server 1 x client 1` 强制密文：`PASS` — `HS_OK_MTLS` 且 `tls` 成功
- **AC-4** 缺 `cert_dir` 失败不回退：`PASS` — `INVALID_PARAM` 直接失败
- **AC-5** `server 1 want0` 强制失败：`PASS` — `HS_OK_MTLS` 但 `cert_dir` 空即失败

## 分析

- 证据仅 `tls_cert` 单测与 `build`，`rpc` 4 象限 `socketpair` 未落库（`rpc_handshake_test` 已按需求忽略），`AC` 判定依赖 `T0342` 的 `host` 前缀与 `cert_dir` 完备性，前置 `ls host.crt` 已校验
- 无未覆盖 AC，5 条均 `test-suite-v2` 映射

## 适用边界

- 仅 `rpc` 首阶段按需/强制，不改 `libs` 与 `sec_*`
- `server 0` 有 `cert_dir` 才按需 `MTLS`，空则固定 `PLAIN`

## 下一轮建议

- 补 `rpc/tests/mixed_mtls` 独立用例以替代已删 `libs` 用例的 `rpc` 侧覆盖
