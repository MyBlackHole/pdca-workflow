# 审查报告：服务端 tls-algorithm 语义（T3960）

## 审查问题

服务端设置 `tls-algorithm` 后是否代表**只支持此算法**？

## 结论

**否。`tls-algorithm` 是协商偏好，不构成算法白名单约束。** 服务端实际支持的算法集由 cert_dir 内部署的证书决定。

## 证据链（四模块协商层）

| 模块 | 位置 | 协商逻辑 |
|------|------|---------|
| rpc (aio-speedd) | rpc/rpc-protocol.cpp:208-215 `hs_negotiate_algorithm` | 仅校验客户端 halg ∈ {SM4=1, AES=2}，`*negotiated = client_alg`；配置值不参与。注释明确"未知/非法算法直接拒绝，不再回落服务端配置" |
| rdbcomm (rdbcommd) | rdbcomm/server.c:497-516 | 同构：`rdb_hs_algorithm_name(halg)` 白名单校验，未知值回 RDB_HS_ERR_ALGORITHM；合法值直接采纳 |
| dmsbtex | dmsbtex/network.c:198-248 `dm_server_handshake` | `(void)cfg`；`dm_hs_algorithm_name(algorithm)` 白名单校验后按客户端算法取 ca_cn |
| libobk (FileTransferAgent) | libobk/lib/logic/oracleCmdTbl.c:92-148 `sbt_session_server_handshake` | 显式 `(void)cfg`；同构白名单校验 + 按客户端算法握手 |

## 证书层事实（决定实际支持集）

libs/tls_cert.c:361-401 `tls_cert_build_server_profiles`：**固定构建双算法 profile**——
- profile 0（SM4）：`sm2_ca.crt / sm2_host.crt / sm2_host.key`
- profile 1（AES/ED25519）：`ed25519_ca.crt(优先)/ca.crt 回退、ed25519_host.crt/host.key`

即服务端 ctx 与 tls-algorithm 配置无关地加载目录内全部可用算法证书；协商成功与否取决于该算法证书是否存在（缺失时握手期以 HS_ERR_CA_CN 拒绝）。

## 配置值的真实用途

1. **客户端侧**：发起协商时携带的默认算法偏好。
2. **服务端侧**：仅剩 ini/env 合法性校验与日志展示；rpc 旧回落路径已被 hs_negotiate_algorithm 替代移除。

## 风险提示

运维直觉"设 tls-algorithm=SM4 = 锁死 SM4"与实际不符——cert_dir 同时部署两套证书时，客户端可协商任一算法。若合规场景需单算法锁定（如强制 AES 或强制 SM4），当前无配置手段。

## 改进建议（未实施，如需另立任务）

1. **单算法锁定语义**：服务端协商层在白名单校验前增加"配置过滤"——cfg.algorithm 非零时仅接受等于配置值的 halg，否则回 HS_ERR_ALGORITHM。四模块同步实施 + e2e 断言（错配算法被拒）。
2. **最低成本替代**：usage/文档明示当前语义为"协商偏好"，避免误解。
