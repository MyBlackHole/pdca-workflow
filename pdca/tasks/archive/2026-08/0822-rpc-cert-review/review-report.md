---
schema: pdca.asset/v1
id: T0348-0822-rpc-cert-review
phase: review
---

# rpc 证书实现审查报告（T0348）

## 审查范围

- `rpc/rpc-server.cpp` 握手分流（mtls 开关 / want_mtls / 算法协商 / ca_cn 下发）
- `rpc/rpc-io.cpp` 客户端握手与降级路径
- `rpc/main.cpp` 证书初始化时机
- `libs/tls_cert.c` slot/CA_CN/诊断日志
- `rpc/tests/mixed_mtls_{test,integration}.cpp` 覆盖度

## 发现（按风险排序）

### F1 高 — client mtls=1 可被静默降级明文

`rpc/rpc-io.cpp:130`：server 回 `HS_OK_PLAIN` 时 client 直接 `return 0` 明文继续。
当 `client mtls=1`（用户显式要求密文）而 `server 0 无 sctx` 回 PLAIN 时，client 静默接受降级，
违反"客户端要求密文即必须密文"的语义；密文数据可能以明文发出且无告警。

**修复**：client 收 `HS_OK_PLAIN` 时检查自身 `g_rpc_config->mtls_enabled`，为 1 则
ErrorLog "server downgraded to plain but mTLS requested" 并失败退出。

### F2 中 — ca_cn 回落值可能为空仍下发

`rpc/rpc-server.cpp:270/311`：`tls_cert_get_ca_cn` 返回 NULL 时回落 `g_rpc_config->ca_cn`
（默认空串），导致下发空 ca_cn，client 三元组校验失败——但错误发生在 client 侧且信息模糊。

**修复**：cn 为空时 server 直接回 `HS_ERR_CA_CN` 并 ErrorLog 实际 cert_dir 与算法，
把错误留在 server 侧可诊断位置。

### F3 中 — server0 按需 MTLS 的 sctx 算法槽缺失无提示

`sctx` 由双算法构建；若 cert_dir 只放了单算法文件，init 即失败（T0342 行为），但
`main.cpp:409` 在 `cert_dir[0]` 为真时 init 失败直接 exit —— `mtls=0 + 坏证书目录`
会导致服务端完全无法启动（连明文都不能服务）。

**修复**：`mtls_enabled=0` 时证书 init 失败降级为 WarningLog + `sctx=NULL`
（服务端以纯明文继续），`mtls_enabled=1` 时保持 exit。启动日志明确输出当前模式。

### F4 低 — mixed_mtls_integration 未断言 client 实际使用 ca_cn 定位到证书

AC-2 断言了响应含非空 ca_cn，但未校验 `cert_dir/<ca_cn>/host.*` 存在。
补一条前置 `access()` 断言即可闭环。

### F5 信息 — GET_TIME 明文放行窗口

`server 1` 下 `MT_GET_TIME` 有意放行明文（设计使然），无泄露风险但应在 help/文档标注。

## 通过项

- 算法协商采纳客户端值、非法回落 ✓
- 双重握手防护（handshake_done）✓
- server TLS 握手失败不降级、直接断开 ✓
- client 三元组完备性校验 ✓
- 证书异常双层诊断日志（T0346 交付）✓
- 项目内证书约束落地、sm2_client/client-001/002 已清理 ✓

## 处置建议

F1/F2/F3 建议立独立 development 任务修复（预计 3 文件小改动）；
F4 随任一相关任务顺手带上；F5 文档化即可。
