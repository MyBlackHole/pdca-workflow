# T0358 测试证据 2026-08-22T20:35:26+08:00

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

## 工具端到端拒绝验证
rdbcomm(RDBCOMM_TLS_ALGORITHM=sm2) exit=1
aio-speedd(AIO_SPEEDD_TLS_ALGORITHM=x) exit=1
