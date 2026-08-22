# T0360 证据 — 死字段清理与保留字段消费点审计

日期：2026-08-22　提交：（见 git log）

## 已删除字段（填充后零消费，共 5 结构体 22 字段 + 2 个 unused 函数）

| 结构体 | 删除字段 | 连带删除 |
|--------|---------|---------|
| rpc `g_rpc_config` | ca_cn / ca_cert / client_cert / client_key / server_cert / server_key | rpc-config.cpp 填充 3 段、rpc-client.cpp 填充 3 段 |
| dmsbtex `_tls_config_t` | 同上六字段 | sbt_tls_config_init 填充 5 段、unused `sbt_client_cert_paths` |
| rdbcomm `client_options`/`rdbcomm_conn` | ca_cn / ca_cert / client_cert / client_key | main 填充 3 段、client.c 拷贝链 |
| rdbcomm `server_options` | ca_cn / ca_cert / server_cert / server_key / tls_algorithm(M4) | rdbcommd-main.c 填充 4 段 |
| libobk `sbtctx` | tls_ca_cn / tls_ca_cert / tls_client_cert / tls_client_key | init 填充 3 段、unused `sbt_client_cert_paths` |

## 保留字段消费点审计（AC-3）

| 字段 | 消费点（file:line） |
|------|-------------------|
| rpc `cert_dir` | rpc/main.cpp:409-412、rpc/rpc-io.cpp:145,150 |
| rpc `mtls_enabled` | rpc-server.cpp:253、rpc-io.cpp:86,100 |
| rpc `tls_algorithm` | rpc-io.cpp:107,143、rpc-server.cpp:248 |
| dmsbtex `cert_dir` | network.c sbt_session_client_init/sbt_session_server_prepare |
| dmsbtex `mtls_enabled`/`algorithm(_name)` | network.c 握手路径、main.c |
| rdbcomm `conn->cert_dir` | client.c:204,210（握手证书目录） |
| rdbcomm server `mtls_enabled`/`cert_dir` | server.c:531、rdbcommd-main.c:364-374 |
| libobk `tls_cert_dir` | libobk.c sbt_session_client_init（6 处） |
| libobk `tls_mtls_enabled`/`tls_algorithm(_name)` | libobk.c 握手协商 |

## 测试验证

- 全量构建 ok（xmake -r）
- rpc_own_handshake_test / rdbcomm_handshake_session_test / dmsbtex_session_test / libobk_session_test：PASS
- mixed_mtls_integration：PASS
- 端到端：RDBCOMM_TLS_ALGORITHM=sm2 → rdbcomm exit=1；AIO_SPEEDD_TLS_ALGORITHM=x → aio-speedd exit=1（T0358 校验行为未回归）
