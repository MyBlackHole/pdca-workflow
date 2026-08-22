# 测试结果（AC-3）

## dmsbtex 握手测试

`xmake run dmsbtex_session_test` 输出（节选）：

```
[PASS] dm algorithm exact mapping
[PASS] sbt_tls_config_init fail-closed
[PASS] plain zero-handshake passthrough
[PASS] forced mTLS upgrade
[PASS] bad cert_dir prepare fail
[PASS] no-downgrade reject
[PASS] malformed algorithm fail-closed
[PASS] DM_HS_ERR_CA_CN reject code present
dmsbtex_session_test: ALL PASS
```

新增断言 `[PASS] DM_HS_ERR_CA_CN reject code present` 通过（编译期保证拒绝码可达、帧类型正确）。

## 全量回归

`xmake test`：

```
100% tests passed, 0 test(s) failed out of 40
```

40/40 PASS，含 `dmsbtex_session_test`、`libobk_session_test`、`rdbcomm_handshake_session_test`、`rpc_own_handshake_test`、`mixed_mtls_integration` 等，无回归。

## 覆盖范围说明

`ca_cn unavailable` 运行时分支需"服务端 ctx 有效但证书 ca_cn 为空"的证书环境，由集成测试覆盖；
本修复经 code-review 确认与同文件其他拒绝分支及 rpc/rdbcomm 同构，未引入回归（全量测试实证）。
