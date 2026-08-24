## Do → Check 交接摘要 (2026-08-24)

- 根因：keygen 无 CN 字符集校验 → 存量 CA CN 含空格 → 客户端 tls_cert_ca_cn_valid 拒绝。
- 用户裁决方案：keygen 强制无空格（cn_name_valid 落 common.c，与客户端规则互引）；SM2 布局缺口不处理；客户端校验不动。
- TDD：tls_keygen_test 先红后绿（5/5）；CLI 黑盒含空格 CN 拒绝+合法 CN 通过；重签证书部署后 aio-speed mTLS 实机握手成功（TLS_SM4_GCM_SM3）。
- 回归：tls_cert_test/rdb_config_test/rdbcomm_handshake_session 全绿；rpc_handshake_test 等 3 个为既有环境性失败（stash 基线对照一致，非本次引入）。
- evidence：fix-patch / verify-log / keygen-test-src / convergence-map；validate valid=true。
## Check → Act 交接摘要 (2026-08-24)

- Ch1/Ch3：四 AC 判定 ✅，validate-convergence valid=true。
- Ch5：用户 verdict=confirmed 已落盘（check_confirmation）。
- 行为变更与边界已记入 conclusion 适用边界节。
