---
schema: pdca.asset/v1
id: T0393-0826-dmsbtex-mtls-handshake-enforce
title: dmsbtex: dm_server_handshake 显式按 mtls_enabled 强制 mTLS（F4 一致性）
type: prd
scenario_type: bugfix
parent: T0392
created_at: 2026-08-26T23:20:00+08:00
status: plan
problem: |
  dmsbtex 的 dm_server_handshake（dmsbtex/network.c:204）仅检查 !sbt_server_ctx，不显式检查
  cfg->mtls_enabled。由于 sbt_session_server_prepare（network.c:291）在 cert_dir 有效时无论
  mtls_enabled 与否都会构建 sbt_server_ctx，存在“配置 mtls=0 但握手被实际执行”的隐式不一致；
  mTLS 强制实际依赖 main.c:271 业务帧闸门兜底，与其余三模块（rpc/rdbcomm/libobk）在握手层
  直接依据 mtls_enabled 强制不一致（mTLS 全面审查 F4）。
plan: |
  bugfix：在 dm_server_handshake 起点显式依据 mtls_enabled 决策——mtls 未启用或 ctx 缺失均
  回 DM_HS_ERR_MTLS_UNAVAILABLE 并拒绝握手（fail-closed），与 rpc/rdbcomm/libobk 语义一致。
  main.c:271 业务帧闸门保留为纵深防御。新增 dmsbtex session_test 区分性用例验证。
verification: |
  dmsbtex session_test 新增用例：mtls_enabled=0 但 cert_dir 有效（sbt_server_ctx 已构建）时，
  客户端发起 mTLS 握手必须被服务端拒绝（server_thread exit_code==6）；无修复时握手会成功导致用例失败。
  既有用例（明文直通 / 强制升级 / 无降级拒绝 / 算法锁 / 畸形算法）全过。
ac:
  - id: AC-1
    description: dm_server_handshake 显式检查 cfg->mtls_enabled（mtls=0 或 ctx 缺失均拒绝），与 rpc/rdbcomm/libobk 握手层强制一致。
  - id: AC-2
    description: 新增 session_test 用例（mtls_disabled_rejects_handshake）通过，且具区分性——无修复时握手成功致用例失败。
  - id: AC-3
    description: 既有 dmsbtex session_test 全部用例（AC-3 明文直通 / AC-1 强制升级 / AC-4b 无降级拒绝 / T3961 算法锁 / T0358 畸形算法）无回归。
impact: |
  dmsbtex 服务端握手强制逻辑与全仓库一致；不改变 mtls 启用时的正确握手行为，亦不改变 main.c:271 纵深防御。
---

# dmsbtex dm_server_handshake 显式按 mtls_enabled 强制 mTLS（F4）

## 问题陈述
mTLS 全面审查（T0392）发现 F4：dmsbtex 的 mTLS 强制逻辑分散且不在握手函数内显式检查 `mtls_enabled`。

- `dm_server_handshake`（`dmsbtex/network.c:204`）只检查 `!sbt_server_ctx` 返回 `DM_HS_ERR_MTLS_UNAVAILABLE`，**不读 `cfg->mtls_enabled`**。
- `sbt_session_server_prepare`（`network.c:291`）在 `cert_dir` 非空时**无论 `mtls_enabled` 与否都会构建 `sbt_server_ctx`**（仅 `mtls_enabled && ret!=0` 才报错）。
- 因此当 `mtls_enabled=0` 但 `cert_dir` 有效时，服务端 `sbt_server_ctx` 非 NULL，`dm_server_handshake` 会实际执行真实 mTLS 握手——与"mTLS 已关闭"的声明不一致；真正的强制依赖 `main.c:271` 业务帧闸门兜底。
- 其余三模块（rpc / rdbcomm / libobk）均在握手层直接依据 `mtls_enabled` 强制，语义一致。

## 修复方案
在 `dm_server_handshake` 起点将内核判定改为：
```c
/* F4（T0393）：显式依据 mtls_enabled 强制，与 rpc/rdbcomm/libobk 一致。
 * mTLS 未启用或上下文缺失均拒绝握手（不允许“配置关却实际握手”）。 */
if (!sbt_server_ctx || !cfg->mtls_enabled) {
    ... 回 DM_HS_ERR_MTLS_UNAVAILABLE，return -1;
}
```
`main.c:271` 业务帧闸门保留为纵深防御，不改动。

## 验证
- 新增 `dmsbtex/test/session_test.c` 用例：构造 `mtls_enabled=0` + 有效 `cert_dir` 并 `sbt_session_server_prepare` 成功（ctx 已构建），客户端 `mtls_enabled=1` 发起握手 → 服务端必须拒绝（`exit_code==6`）。
- 该用例具区分性：无修复时 ctx 存在且未检查 `mtls_enabled`，握手会成功 → 用例失败。
- 既有用例全过（无回归）。

## 范围外
- 不改动 rpc/rdbcomm/libobk（已正确）。
- 不改动 `main.c:271` 纵深防御逻辑。

## 验收标准
- [ ] AC-1: `dm_server_handshake` 显式检查 `cfg->mtls_enabled`（mtls=0 或 ctx 缺失均拒绝）。
- [ ] AC-2: 新增 session_test 区分性用例通过。
- [ ] AC-3: 既有 dmsbtex session_test 全过，无回归。
