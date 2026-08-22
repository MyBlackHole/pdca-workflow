# T0361 测试证据 2026-08-22T21:54:33+08:00

## rdb_config_test
Running parse_and_get_int... PASSED
Running config_get_int_default... PASSED
Running config_get_string... PASSED
Running config_get_string_null_for_missing... PASSED
Running config_get_string_global_fallback... PASSED
Running config_set_string... PASSED
Running config_section_count_and_entry... PASSED
Running parse_nonexistent_file... PASSED
Running init_config_from_env... PASSED
Running parse_config_twice... PASSED
Running config_get_int_trailing_spaces... PASSED
Running tool_tls_config_isolated_and_prioritized... PASSED
Running sec_resolve_bool_layers... PASSED
=== 13 passed, 0 failed ===

## rpc_own_handshake_test
[PASS] handshake codec
[PASS] handshake_resp codec
[PASS] algorithm mapping
[PASS] plain both disabled
[PASS] server mTLS reject plain
[PASS] client mtls rejected downgrade to plain
rpc_own_handshake_test: ALL PASS

## rdbcomm_handshake_session_test
[PASS] rdb algorithm exact mapping
[PASS] plain zero-handshake passthrough
[PASS] rdb algorithm exact mapping
[PASS] plain zero-handshake passthrough
[PASS] on-demand mTLS upgrade
[PASS] reject without downgrade
rdbcomm_handshake_session_test: ALL PASS

## dmsbtex_session_test
[PASS] dm algorithm exact mapping
[PASS] sbt_tls_config_init fail-closed
[PASS] plain zero-handshake passthrough
[PASS] forced mTLS upgrade
[PASS] bad cert_dir prepare fail
[PASS] no-downgrade reject
dmsbtex_session_test: ALL PASS

## libobk_session_test

## mixed_mtls_integration
AC-1 plain plain PASS
AC-1 plain plain PASS
AC-2 mixed on-demand mTLS PASS
AC-2 mixed on-demand mTLS PASS
AC-3 forced mTLS PASS
AC-3 forced mTLS PASS
AC-4 missing client cert_dir fail PASS
AC-4 missing client cert_dir fail PASS
AC-5 server forced reject plain business PASS
AC-6 no-downgrade PASS
AC-7 plain-only startup PASS
mixed_mtls_link_integration: PASS

## 端到端
rdbcomm env=abc exit=$?=1
rdbcommd env=abc exit=1
aio-speedd alg非法 exit=1
aio-speed CLI非法 exit=1
rdbcommd ini(tls_enable=1) 生效 exit=2 (mTLS模式无证书退出≠常驻)

## 补漏提交 2456402（用户发现 oracleCmdTbl.c:36 残留后修复）

- libobk 服务端入口 sbt_server_tls_config_init：atoi fail-open → sec_resolve_bool + 算法名规范校验
- libobk_tls_config_t 删除 T0360 未审计死字段 6 个（ca_cn/ca_cert/client_cert/client_key/server_cert/server_key）
- 终检：全仓 atoi(v)!=0 残留 = 0；getenv+atoi 无残留
- 回归：全量构建 ok，六套测试 PASS（含 mixed_mtls_integration）
