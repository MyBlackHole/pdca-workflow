# 审查：服务端设置 tls-algorithm 后是否代表只支持此算法

## 问题

用户疑问：服务端（aio-speedd/rdbcommd/dmsbtex/FileTransferAgent）设置 `tls-algorithm` 后，是否代表只支持此算法。

## 审查结论

**否。`tls-algorithm` 不限制服务端实际支持的算法集，仅是协商偏好。**

四模块服务端协商逻辑同构（rpc-server.cpp:252-258 / rdbcomm/server.c:497-516 / dmsbtex/network.c:198-248 / libobk oracleCmdTbl.c:92-148）：

1. **协商层**：只校验客户端 halg 是否在白名单（SM4=1/AES=2 二选一），未知值拒绝（HS_ERR_ALGORITHM，T0357/T0358 fail-closed 语义）；合法值直接采纳客户端选择——**服务端配置的 tls-algorithm 完全不参与协商约束**（libobk 的 `sbt_session_server_handshake` 甚至显式 `(void)cfg`）。
2. **证书层**：`tls_cert_build_server_profiles`（tls_cert.c:361-401）固定构建双算法 profile（SM4→sm2_*、AES→ed25519_*），cert_dir 部署了哪个算法的证书就实际能完成哪个算法的 TLS 握手；缺失时握手期以 HS_ERR_CA_CN 拒绝。
3. **配置值的真实用途**：客户端发起协商时携带的默认偏好；服务端旧"回落服务端配置"路径已移除（rpc 注释"不再回落服务端配置"，T0358）。

### 风险提示

运维直觉"设 tls-algorithm=SM4 = 锁死 SM4"与实际不符——只要 cert_dir 内存在对应算法证书，客户端可协商任一算法。若合规场景需**单算法锁定**（禁用另一算法），当前无配置手段。

### 建议（不在本任务实施）

- 如需单算法锁定语义：服务端协商层增加"配置算法白名单过滤"（配置非空时仅接受该算法，其余回 HS_ERR_ALGORITHM），并同步 e2e 断言。
- 或至少在 usage/文档明确当前语义为"协商偏好而非白名单"。

## 验收标准

- [ ] AC-1: 审查报告落盘且覆盖四模块协商层代码位置引用。
- [ ] AC-2: 结论含证书层双 profile 事实依据（tls_cert.c 行号）与风险提示。
