---
schema: pdca.asset/v1
id: T0361-0822-mtls-param-unify
phase: check
source_ids: [evidence-test, evidence-test-v2]
---

## 上下文

用户两项意见落地：(1) cli_mtls_set/cli_mtls_enabled 双字段精简；(2) 各工具 mtls_enabled 统一走 sec_resolve 分层解析（配置打底、CLI 覆盖）。development 场景。

## 假设与结果

| 假设 | 结果 |
|---|---|
| 双字段可用单一三态载体替代 | 成立且更进一步：rdbcomm-main 经 copts.mtls_enabled 一字段三用（配置打底→getopt 覆盖→校验消费），cli 意图字段全仓清零 |
| 统一解析需严格布尔底座 | 成立：新增 sec_resolve_bool（分层同 sec_resolve_int，仅收 "0"/"1"，非法 -1 哨兵） |
| dmsbtex/libobk 可接入 ini | 成立：删除 T0358 临时 parse_bool_env，SBT_MTLS_ENABLE 与 [security] tls_enable 双通道生效 |
| 全部 mtls 解析点已收敛 | **修正×2**：Check 阶段用户先后发现 (a) oracleCmdTbl.c atoi fail-open 第三处遗漏（补漏 2456402，连带清理 libobk_tls_config_t 六死字段）；(b) xmake test 全量重建失败——libobk_session_test 三处测试文件遗漏被增量构建连续掩盖（规范名误入非法列表、env 残留污染、T0360 已删字段断言残留），修复 4bb3c8a 后 xmake test 40/40 PASS |

## 分析

- **AC-1 通过**：cli_mtls_set 全仓 grep 为零
- **AC-2 通过**：sec_resolve_bool_layers 单测覆盖 env 合法/非法/空串、ini 两层、默认值（13 passed）
- **AC-3 通过**：端到端 env 非法 exit=1（rdbcomm/rdbcommd）、CLI 非法 exit=1（aio-speed/aio-speedd）、ini tls_enable=1 使 rdbcommd 进入 mTLS 模式（exit=2 无证书退出≠常驻）
- **AC-4 通过**：六套测试 PASS；dmsbtex_session_test 连续 10 次 PASS（顺手修复缺失 SIGPIPE 忽略的既有 flaky，exit=141）

Grill 自检：
1. 覆盖完整性曾被证伪一次——用户指出 oracleCmdTbl.c:36 残留，暴露"按结构体前缀 grep"方法的盲区（libobk 服务端独立入口）；补漏后改用 atoi(v) 全仓扫描终检=0
2. 行为变更——dmsbtex/libobk 新增 ini 配置能力属增强；[security] tls_enable 非 0/1 将启动失败为 fail-closed 设计意图
3. 附带发现——T0360 两处遗漏（libobk_tls_config_t 死字段、make_cfg ca_cert 残留引用被增量构建掩盖）均已修复并在提交信息中披露

## 适用边界

- 通用 sec_resolve_int / config_get_int 的 atoi 行为未动（非布尔调用方影响面大）
- 协商白名单归 T0357

## 下一轮建议

- T0357 实施时复用 sec_resolve_bool 做 mtls 相关校验；审计方法改为"按函数入口全量扫描 getenv+atoi 组合"
- 流程教训：Do 阶段回归验证必须以 running tests ...
[0m[38;2;0;255;0;1m[  0%]:[0m running.test access/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test chmod/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test chown/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test dir_tree/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test dir_utils_dir_copy_test/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test dmsbtex_session_test/default[0m
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4329 rpc_conn_srv_chmod|139807063795392| chmod /tmp/tmp1/cv_debug:511 success.
[0m[38;2;0;255;0;1m[  0%]:[0m running.test download_fileat/default[0m
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4377 rpc_conn_srv_chown|140508238177984| chmod /tmp/tmp1/cv_debug:1000 success.
[0m[38;2;0;255;0;1m[  0%]:[0m running.test download_fileats/default[0m
/tmp/rpc_dir_tree_test/file1.txt
/tmp/rpc_dir_tree_test/sub1/file2.txt
[0m[38;2;0;255;0;1m[  0%]:[0m running.test download_file/default[0m
[PASS] dm algorithm exact mapping
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:110 sbt_tls_config_init|140120398263168| tls config: invalid SBT_MTLS_ENABLE value (expect "0"/"1")
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:110 sbt_tls_config_init|140120398263168| tls config: invalid SBT_MTLS_ENABLE value (expect "0"/"1")
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:110 sbt_tls_config_init|140120398263168| tls config: invalid SBT_MTLS_ENABLE value (expect "0"/"1")
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:118 sbt_tls_config_init|140120398263168| tls config: unknown tls_algorithm "sm2"
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:118 sbt_tls_config_init|140120398263168| tls config: unknown tls_algorithm "SM2"
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:118 sbt_tls_config_init|140120398263168| tls config: unknown tls_algorithm "TLS_AES_256_GCM_SHA384Y"
[0m[38;2;0;255;0;1m[  0%]:[0m running.test download_file_dir/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test download_link/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test execute_command/default[0m
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3849 rpc_conn_srv_download_fileats|139718972925632| openat test1.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3878 rpc_conn_srv_download_fileats|139718972925632| read test1.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3849 rpc_conn_srv_download_fileats|139718972925632| openat test2.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3878 rpc_conn_srv_download_fileats|139718972925632| read test2.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:1138 rpc_scp_download|140407186912960| begin download file [/tmp/test_scp_download_file_src]
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:1322 rpc_scp_download|140407186912960| download file [/tmp/test_scp_download_file_src] complete success, send_bytes: 30, f_size: 30
[2026-08-22 22:49:36]|Info|rpc/rpc.cpp:2815 rpc_conn_cli_download_fileats|139718981318336| download_fileat /tmp/download_fileats_wvfBrh/src/:test1.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc.cpp:2815 rpc_conn_cli_download_fileats|139718981318336| download_fileat /tmp/download_fileats_wvfBrh/src/:test2.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-command.cpp:236 do_scp_download|140407178520256| scp download [/tmp/test_scp_download_file_dst from /tmp/test_scp_download_file_src], status completed success, elapse 1 s, f_size 30 bytes, recv 30 bytes, 0.00 M/s
[0m[38;2;0;255;0;1m[  0%]:[0m running.test fchmodats/default[0m
[0m[38;2;0;255;0;1m[  0%]:[0m running.test fchownats/default[0m
test [download_file_exists] PASSED
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:1138 rpc_scp_download|140407178520256| begin download file [/nonexistent/remote]
[2026-08-22 22:49:36]|Warning|rpc/rpc-server.cpp:1157 rpc_scp_download|140407178520256| local_file: [/nonexistent/remote] not existed, errno:2)
[2026-08-22 22:49:36]|Warning|rpc/rpc-server.cpp:1173 rpc_scp_download|140407178520256| local_file: [/nonexistent/remote] not existed.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:1322 rpc_scp_download|140407178520256| download file [/nonexistent/remote] complete success, send_bytes: 0, f_size: 0
[2026-08-22 22:49:36]|Info|rpc/rpc-command.cpp:236 do_scp_download|140407186912960| scp download [/tmp/test_scp_download_file_dst2 from /nonexistent/remote], status completed success, elapse 1 s, f_size 0 bytes, recv 0 bytes, 0.00 M/s
[2026-08-22 22:49:36]|Info|rpc/rpc-command.cpp:461 do_scp_download_link|139769438791360| scp download link [/tmp/test_scp_download_link_src -> /tmp/test_scp_download_link_out] success
[0m[38;2;0;255;0;1m[  0%]:[0m running.test fs_meta_comprehensive_test/default[0m
[PASS] sbt_tls_config_init fail-closed
[PASS] plain zero-handshake passthrough
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140120398263168| Applied ciphersuites config: TLS_SM4_GCM_SM3
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3758 rpc_conn_srv_fchmodats|140284539168448| fchownat test_chmod.txt:508 success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3758 rpc_conn_srv_fchmodats|140284539168448| fchownat test_chmod2.txt:493 success.
[0m[38;2;0;255;0;1m[  0%]:[0m running.test libobk_session_test/default[0m
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:852 execute_cmd|139630307436224| execute:[cmd_len:35, command:echo 'execute_shell_script_test_ok']
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:1011 my_popen|139630307436224| cmd echo 'execute_shell_script_test_ok' pipe[0]:9, pipe[1]:10
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3670 rpc_conn_srv_fchownats|140695574668992| fchownat test_chown.txt:1000:1000 success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3670 rpc_conn_srv_fchownats|140695574668992| fchownat test_chown2.txt:1000:1000 success.
test [download_not_exist_api_stat_0] PASSED
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:1138 rpc_scp_download|140407186912960| begin download file [/nonexistent/remote]
[2026-08-22 22:49:36]|Warning|rpc/rpc-server.cpp:1157 rpc_scp_download|140407186912960| local_file: [/nonexistent/remote] not existed, errno:2)
[2026-08-22 22:49:36]|Error|rpc/rpc-command.cpp:139 do_scp_download|140407178520256| download /nonexistent/remote failure
[2026-08-22 22:49:36]|Error|rpc/rpc-server.cpp:1178 rpc_scp_download|140407186912960| local_file: [/nonexistent/remote] not existed.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:866 execute_cmd|139630307436224| generate subprocess: 499943
[0m[38;2;0;255;0;1m[  0%]:[0m running.test lmdb_dict_test/default[0m
test [download_not_exist_api_stat_1] PASSED
[0m[38;2;0;255;0;1m[  0%]:[0m running.test lmdb_sort_test/default[0m
开始测试目录复制功能...
测试目录: /tmp/aio/rpc/rpc_test
目标目录: /tmp/aio/rpc/copy_test
返回值: 0
[2026-08-22 22:49:36]|Warning|rpc/rpc-server.cpp:927 execute_cmd|139630307436224| execute_shell_script_test_ok

execute_shell_script_test_ok
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:948 execute_cmd|139630307436224| [echo 'execute_shell_script_test_ok'] completed, return value:0
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140120398263168| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
========================================
       FsMeta Test Suite
========================================

=== TEST: TYPE_UPDATE - Fragmented ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_06
execute_shell_script test PASSED
[0m[38;2;0;255;0;1m[  2%]:[0m running.test logger_test/default[0m
[0m[38;2;0;255;0;1m[  5%]:[0m running.test LRUCache_test/default[0m
[0m[38;2;0;255;0;1m[  7%]:[0m running.test lstat/default[0m
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140120398263168| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
Running logger tests...
Tests passed: 11, failed: 0
[0m[38;2;0;255;0;1m[ 10%]:[0m running.test metadata/default[0m
PASS

=== TEST: TYPE_UPDATE - 1M File Overwrite at 500K ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_27
[0m[38;2;0;255;0;1m[ 12%]:[0m running.test mixed_mtls_integration/default[0m
[0m[38;2;0;255;0;1m[ 15%]:[0m running.test mixed_mtls_test/default[0m
/proc/self/exe: size=0, mode=120777, atime=1787410176, mtime=1787410176, ctime=140416904205377
[0m[38;2;0;255;0;1m[ 17%]:[0m running.test mkdirall/default[0m
PASS

=== TEST: TYPE_NEW - Small File (Full Download) ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_01
[0m[38;2;0;255;0;1m[ 20%]:[0m running.test mkdir/default[0m
AC-1 server0/want0 -> PLAIN PASS
AC-4 server1/no-cert -> REQUIRED PASS
skip AC-2/3/5: no certs in libs/tests/certs
mixed_mtls: PASS (partial)
[0m[38;2;0;255;0;1m[ 22%]:[0m running.test mkdir_path_test/default[0m
[0m[38;2;0;255;0;1m[ 25%]:[0m running.test pread/default[0m
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4283 rpc_conn_srv_mkdirall|140200047011520| mkdirall /tmp/tmp1/cv_debug:0 success.
PASS

=== TEST: TYPE_NEW - Write Zero ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_02
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:3595 rpc_conn_srv_mkdir|139847408805568| mkdir /tmp/tmp1/cv_debug:511 success.
[0m[38;2;0;255;0;1m[ 27%]:[0m running.test pwrite/default[0m
AC-1 plain plain PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_SM4_GCM_SM3
[0m[38;2;0;255;0;1m[ 30%]:[0m running.test rdbcomm_handshake_session_test/default[0m
[0m[38;2;0;255;0;1m[ 32%]:[0m running.test rdb_config_test/default[0m
do_remote_pread success
[PASS] forced mTLS upgrade
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140120398263168| Applied ciphersuites config: TLS_SM4_GCM_SM3
[2026-08-22 22:49:36]|Error|libs/tls_cert.c:75 tls_cert_log_setup_error|140120398263168| TLS setup failed: role=server stage=ca-certificate algorithm=TLS_SM4_GCM_SM3 ca=/nonexistent/certs/sm2_ca.crt cert=/nonexistent/certs/sm2_host.crt key=/nonexistent/certs/sm2_host.key
[PASS] bad cert_dir prepare fail
[2026-08-22 22:49:36]|Error|dmsbtex/network.c:212 dm_server_handshake|140120390891200| handshake: no TLS context, reject
[PASS] no-downgrade reject
dmsbtex_session_test: ALL PASS
PASS

=== TEST: TYPE_UPDATE - Basic ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_03
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[0m[38;2;0;255;0;1m[ 35%]:[0m running.test readdir/default[0m
do_remote_pwrite success
[0m[38;2;0;255;0;1m[ 37%]:[0m running.test readdir_tree/default[0m
=== rdb-config test ===

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
PASS

=== TEST: TYPE_UPDATE - Within Size ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_04
[0m[38;2;0;255;0;1m[ 40%]:[0m running.test readlink/default[0m
=== 手动事务示例 ===
批量写入完成，共100条记录
批量读取完成，找到 100/100 条记录

=== 游标遍历示例 ===
正向遍历:
  Key: cursor_key_0, Value: cursor_value_0
  Key: cursor_key_1, Value: cursor_value_1
  Key: cursor_key_2, Value: cursor_value_2
  Key: cursor_key_3, Value: cursor_value_3
  Key: cursor_key_4, Value: cursor_value_4
AC-1 plain plain PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[0m[38;2;0;255;0;1m[ 42%]:[0m running.test rpc_net_time_test/default[0m
[0m[38;2;0;255;0;1m[ 45%]:[0m running.test rpc_own_handshake_test/default[0m
[PASS] rdb algorithm exact mapping
[PASS] plain zero-handshake passthrough
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140252424266624| Applied ciphersuites config: TLS_SM4_GCM_SM3
====================================
  LMDB 默认排序 (memcmp) 验证测试
====================================

=== 测试 1: LMDB 默认字典序 (路径 key) ===
  遍历结果:
    [0] key='/a'
    [1] key='/a/b'
    [2] key='/a/bb'
    [3] key='/a/bb/c'
    [4] key='/a/bc'
    [5] key='/a/c'
    [6] key='/aa'
  ✓ 字典序验证通过: 7 个 key 按正确顺序排列

=== 测试 2: 子路径连续性 (目录分组) ===
  遍历结果:
    [0] key='/'
    [1] key='/a'
    [2] key='/a/b'
    [3] key='/a/b/c'
    [4] key='/a/b/d'
    [5] key='/a/c'
    [6] key='/b'
    [7] key='/b/a'
    [8] key='/ba'
  /a 的子路径范围: [2..5]
    '/a/b' — starts with '/a/'
    '/a/b/c' — starts with '/a/'
    '/a/b/d' — starts with '/a/'
    '/a/c' — starts with '/a/'
  /b 的子路径范围: [7..7]
    '/b/a' — starts with '/b/'
  ✓ 子路径连续性验证通过

=== 测试 3: null 终止符对排序的影响 ===
  遍历结果:
    [0] key='/a'
    [1] key='/a/b'
    [2] key='/aa'

  关键验证:
    '/a' < '/a/b' :  (0x00) < '/'(0x2f)
                  → 目录自身先于其子路径
    '/a/b' < '/aa' : '/'(0x2f) < 'a'(0x61)
                  → 子路径先于同名前缀兄弟

  ✓ null 终止符排序影响验证通过

====================================
  全部测试通过!
====================================
PASS

=== TEST: TYPE_UPDATE - Extend (size_ext - size) ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_05
[0m[38;2;0;255;0;1m[ 47%]:[0m running.test rpc_tool_integration/default[0m
lmdb_sort_test: size=80, mode=40755, atime=1787410176, mtime=1787410176, ctime=140723561805927
pread_test_dst.bin: size=29, mode=100644, atime=1787410176, mtime=1787410176, ctime=140723561805927
rpc_metadata_test_hA0Hb1: size=80, mode=40700, atime=1787410176, mtime=1787410176, ctime=140723561805927
fchownats_test_nHqu0e: size=80, mode=40700, atime=1787410176, mtime=1787410176, ctime=140723561805927
fchmodats_test_jnwpeL: size=80, mode=40700, atime=1787410176, mtime=1787410176, ctime=140723561805927
download_fileats_wvfBrh: size=80, mode=40700, atime=1787410176, mtime=1787410176, ctime=140723561805927
upload_fileats_DLtnQ1: size=80, mode=40700, atime=1787410062, mtime=1787410062, ctime=140723561805927
rpc_metadata_test_0rqQ09: size=80, mode=40700, atime=1787410062, mtime=1787410062, ctime=140723561805927
fchownats_test_0Iqc6m: size=80, mode=40700, atime=1787410062, mtime=1787410062, ctime=140723561805927
fchmodats_test_WvYWek: size=80, mode=40700, atime=1787410062, mtime=1787410062, ctime=140723561805927
download_fileats_fDkNZB: size=80, mode=40700, atime=1787410062, mtime=1787410062, ctime=140723561805927
upload_fileats_FtpZRx: size=80, mode=40700, atime=1787410026, mtime=1787410026, ctime=140723561805927
rpc_metadata_test_r4JGMQ: size=80, mode=40700, atime=1787410026, mtime=1787410026, ctime=140723561805927
fchownats_test_GvDAuB: size=80, mode=40700, atime=1787410026, mtime=1787410026, ctime=140723561805927
fchmodats_test_IE3uEc: size=80, mode=40700, atime=1787410026, mtime=1787410026, ctime=140723561805927
download_fileats_C0KaaE: size=80, mode=40700, atime=1787410026, mtime=1787410026, ctime=140723561805927
t0361_dbg.c: size=519, mode=100644, atime=1787409795, mtime=1787409466, ctime=140723561805927
upload_fileats_tyoKP2: size=80, mode=40700, atime=1787409420, mtime=1787409420, ctime=140723561805927
rpc_metadata_test_tkFq4U: size=80, mode=40700, atime=1787409420, mtime=1787409420, ctime=140723561805927
fchownats_test_uUTBkN: size=80, mode=40700, atime=1787409420, mtime=1787409420, ctime=140723561805927
fchmodats_test_HS4Q56: size=80, mode=40700, atime=1787409420, mtime=1787409420, ctime=140723561805927
download_fileats_VnCOCh: size=80, mode=40700, atime=1787409420, mtime=1787409420, ctime=140723561805927
upload_fileats_sCe8t5: size=80, mode=40700, atime=1787408717, mtime=1787408717, ctime=140723561805927
rpc_metadata_test_fRpab2: size=80, mode=40700, atime=1787408717, mtime=1787408717, ctime=140723561805927
fchownats_test_Q6M0JX: size=80, mode=40700, atime=1787408717, mtime=1787408717, ctime=140723561805927
fchmodats_test_PODW4T: size=80, mode=40700, atime=1787408717, mtime=1787408717, ctime=140723561805927
download_fileats_3AjZsE: size=80, mode=40700, atime=1787408717, mtime=1787408717, ctime=140723561805927
preamble-f57d45.pch: size=4612224, mode=100644, atime=1787410001, mtime=1787408673, ctime=140723561805927
ccgzLeFK.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccoEoRub.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
cc3L0oKc.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccWR3gas.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccEeCiRe.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
cc6MrY1H.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccu7ygUe.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccZFiQUk.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccsyu77m.s: size=778545, mode=100600, atime=1787408549, mtime=1787408550, ctime=140723561805927
cc1Bzckl.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccnMW1e5.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccRrXAtp.s: size=431490, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
ccQesmhj.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
cccNoI1R.res: size=0, mode=100600, atime=1787408549, mtime=1787408549, ctime=140723561805927
cc7PTvIq.res: size=0, mode=100600, atime=1787408548, mtime=1787408548, ctime=140723561805927
ccgJEd7R.s: size=30998, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
ccMvBk3m.s: size=431635, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
cclIhvEF.s: size=432182, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
ccl81nwH.s: size=429468, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
cclMU1L0.s: size=73449, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
ccYStolA.s: size=92296, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
ccKfNQ6s.s: size=429188, mode=100600, atime=1787408491, mtime=1787408493, ctime=140723561805927
cc6KLr9P.s: size=433793, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
cchZvf8e.s: size=130847, mode=100600, atime=1787408491, mtime=1787408492, ctime=140723561805927
ccoxX8L3.s: size=5117141, mode=100600, atime=1787408490, mtime=1787408494, ctime=140723561805927
ccGzDH5z.s: size=3448648, mode=100600, atime=1787408490, mtime=1787408494, ctime=140723561805927
ccfrnMQt.s: size=4666100, mode=100600, atime=1787408489, mtime=1787408494, ctime=140723561805927
cc61upmS.s: size=1857811, mode=100600, atime=1787408489, mtime=1787408492, ctime=140723561805927
ccgYGz0q.s: size=1437142, mode=100600, atime=1787408491, mtime=1787408491, ctime=140723561805927
cce4kSsZ.s: size=431087, mode=100600, atime=1787408467, mtime=1787408468, ctime=140723561805927
preamble-dad15d.pch: size=4281968, mode=100644, atime=1787407588, mtime=1787407561, ctime=140723561805927
f79d601e26a782fd149b3ffb098aae9f-{87A94AB0-E370-4cde-98D3-ACC110C5967D}: size=100, mode=100644, atime=1787407342, mtime=1787407342, ctime=140723561805927
preamble-8f0bd9.pch: size=4642088, mode=100644, atime=1787406765, mtime=1787406657, ctime=140723561805927
preamble-d7f88a.pch: size=4653908, mode=100644, atime=1787406333, mtime=1787406303, ctime=140723561805927
preamble-d21a90.pch: size=10217124, mode=100644, atime=1787406206, mtime=1787406048, ctime=140723561805927
preamble-2ba370.pch: size=7070984, mode=100644, atime=1787405971, mtime=1787405971, ctime=140723561805927
preamble-b7f0ad.pch: size=7548228, mode=100644, atime=1787405914, mtime=1787405900, ctime=140723561805927
preamble-029917.pch: size=942556, mode=100644, atime=1787405884, mtime=1787405884, ctime=140723561805927
preamble-6eef29.pch: size=697356, mode=100644, atime=1787405849, mtime=1787405849, ctime=140723561805927
preamble-faf928.pch: size=4608212, mode=100644, atime=1787405748, mtime=1787404590, ctime=140723561805927
preamble-cad509.pch: size=4535572, mode=100644, atime=1787405621, mtime=1787404420, ctime=140723561805927
preamble-782fe0.pch: size=707904, mode=100644, atime=1787404338, mtime=1787404338, ctime=140723561805927
rdb_config_test_ml1FGg: size=52, mode=100600, atime=1787404295, mtime=1787404295, ctime=140723561805927
preamble-8142f0.pch: size=240692, mode=100644, atime=1787404275, mtime=1787404275, ctime=140723561805927
preamble-48c013.pch: size=705384, mode=100644, atime=1787404236, mtime=1787404215, ctime=140723561805927
preamble-0dc2bb.pch: size=4661772, mode=100644, atime=1787403405, mtime=1787403380, ctime=140723561805927
preamble-23364e.pch: size=4127548, mode=100644, atime=1787403291, mtime=1787403291, ctime=140723561805927
preamble-57f5ba.pch: size=4686700, mode=100644, atime=1787403248, mtime=1787403235, ctime=140723561805927
preamble-2c151f.pch: size=4465364, mode=100644, atime=1787400959, mtime=1787400959, ctime=140723561805927
preamble-b57e6d.pch: size=1004712, mode=100644, atime=1787400757, mtime=1787400723, ctime=140723561805927
preamble-15f4e1.pch: size=5275208, mode=100644, atime=1787400672, mtime=1787400640, ctime=140723561805927
preamble-887049.pch: size=4103148, mode=100644, atime=1787403224, mtime=1787396592, ctime=140723561805927
preamble-a7238c.pch: size=4324520, mode=100644, atime=1787401478, mtime=1787396004, ctime=140723561805927
upload_fileats_4dXk0c: size=80, mode=40700, atime=1787395194, mtime=1787395194, ctime=140723561805927
rpc_metadata_test_JBJ2Oa: size=80, mode=40700, atime=1787395194, mtime=1787395194, ctime=140723561805927
fchownats_test_rWHWND: size=80, mode=40700, atime=1787395194, mtime=1787395194, ctime=140723561805927
fchmodats_test_AMPCuP: size=80, mode=40700, atime=1787395194, mtime=1787395194, ctime=140723561805927
download_fileats_seTs3H: size=80, mode=40700, atime=1787395194, mtime=1787395194, ctime=140723561805927
cclubOFw.s: size=0, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
ccX4ZvFa.s: size=427, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
ccGor6Jq.s: size=1942010, mode=100600, atime=1787395106, mtime=1787395109, ctime=140723561805927
ccpFWi77.s: size=10498878, mode=100600, atime=1787395106, mtime=1787395114, ctime=140723561805927
ccixl7Xs.s: size=3373437, mode=100600, atime=1787395106, mtime=1787395112, ctime=140723561805927
ccaaNS0c.s: size=305733, mode=100600, atime=1787395106, mtime=1787395107, ctime=140723561805927
ccpeRo8v.s: size=9621758, mode=100600, atime=1787395106, mtime=1787395113, ctime=140723561805927
ccRMcJpH.s: size=9950791, mode=100600, atime=1787395106, mtime=1787395113, ctime=140723561805927
ccXjEznL.s: size=5962836, mode=100600, atime=1787395106, mtime=1787395112, ctime=140723561805927
cc6Kthuf.s: size=13667525, mode=100600, atime=1787395106, mtime=1787395115, ctime=140723561805927
ccoDOR9f.res: size=0, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
ccxEBPcy.res: size=0, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
ccwzHfwv.o: size=1256, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
ccX29i0B.s: size=427, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
cctzfGj7.res: size=0, mode=100600, atime=1787395106, mtime=1787395106, ctime=140723561805927
ccCncgYq.s: size=305930, mode=100600, atime=1787395105, mtime=1787395106, ctime=140723561805927
ccFnVgg1.s: size=9956690, mode=100600, atime=1787395105, mtime=1787395113, ctime=140723561805927
ccfq5TRC.s: size=3060900, mode=100600, atime=1787395105, mtime=1787395110, ctime=140723561805927
go-build3977214795: size=60, mode=40700, atime=1787395105, mtime=1787395106, ctime=140723561805927
ccBD5bYa.s: size=1941989, mode=100600, atime=1787395105, mtime=1787395107, ctime=140723561805927
ccCe3IYa.s: size=5963520, mode=100600, atime=1787395105, mtime=1787395111, ctime=140723561805927
ccJ41pFU.s: size=3398421, mode=100600, atime=1787395105, mtime=1787395112, ctime=140723561805927
ccx03dIN.s: size=9627119, mode=100600, atime=1787395105, mtime=1787395113, ctime=140723561805927
ccJONnbY.s: size=13672658, mode=100600, atime=1787395105, mtime=1787395115, ctime=140723561805927
cc2Ggg85.s: size=14990929, mode=100600, atime=1787395105, mtime=1787395115, ctime=140723561805927
cc1xNr7j.s: size=10504388, mode=100600, atime=1787395105, mtime=1787395113, ctime=140723561805927
cceOW2nE.s: size=10673067, mode=100600, atime=1787395105, mtime=1787395113, ctime=140723561805927
go-build680317016: size=60, mode=40700, atime=1787395105, mtime=1787395105, ctime=140723561805927
cc4X27oG.s: size=10498878, mode=100600, atime=1787395053, mtime=1787395060, ctime=140723561805927
ccJdVKds.s: size=3060057, mode=100600, atime=1787395053, mtime=1787395058, ctime=140723561805927
ccJeyn6X.s: size=14985465, mode=100600, atime=1787395053, mtime=1787395061, ctime=140723561805927
ccm0e3li.s: size=1942010, mode=100600, atime=1787395053, mtime=1787395056, ctime=140723561805927
ccFxp1up.s: size=0, mode=100600, atime=1787395053, mtime=1787395053, ctime=140723561805927
ccDNZm93.s: size=3373437, mode=100600, atime=1787395053, mtime=1787395058, ctime=140723561805927
ccaHvdLl.s: size=5962836, mode=100600, atime=1787395053, mtime=1787395058, ctime=140723561805927
cc7Mrvew.s: size=9621758, mode=100600, atime=1787395053, mtime=1787395059, ctime=140723561805927
ccIxgUoe.s: size=10668065, mode=100600, atime=1787395053, mtime=1787395060, ctime=140723561805927
ccZ0ccvL.res: size=0, mode=100600, atime=1787395052, mtime=1787395052, ctime=140723561805927
ccrxPWkV.res: size=0, mode=100600, atime=1787395052, mtime=1787395052, ctime=140723561805927
ccv93Bh7.res: size=0, mode=100600, atime=1787395052, mtime=1787395052, ctime=140723561805927
ccZjAmyq.s: size=221250, mode=100600, atime=1787395052, mtime=1787395053, ctime=140723561805927
ccp0ONZ9.s: size=305930, mode=100600, atime=1787395052, mtime=1787395053, ctime=140723561805927
go-build145537102: size=60, mode=40700, atime=1787395052, mtime=1787395052, ctime=140723561805927
cciymw0u.s: size=3398421, mode=100600, atime=1787395052, mtime=1787395058, ctime=140723561805927
cce7BZnz.s: size=9956690, mode=100600, atime=1787395050, mtime=1787395059, ctime=140723561805927
cctFjeIH.s: size=1941989, mode=100600, atime=1787395050, mtime=1787395053, ctime=140723561805927
ccRw4h8G.s: size=5963520, mode=100600, atime=1787395050, mtime=1787395057, ctime=140723561805927
cctkE9ir.s: size=3060900, mode=100600, atime=1787395049, mtime=1787395055, ctime=140723561805927
ccgT2VF1.s: size=9627119, mode=100600, atime=1787395047, mtime=1787395057, ctime=140723561805927
ccdppIqI.s: size=13672658, mode=100600, atime=1787395045, mtime=1787395058, ctime=140723561805927
ccVS3SkP.s: size=10673067, mode=100600, atime=1787395044, mtime=1787395055, ctime=140723561805927
cclFHxZf.s: size=10504388, mode=100600, atime=1787395044, mtime=1787395055, ctime=140723561805927
ccGbyLdA.s: size=14990929, mode=100600, atime=1787395043, mtime=1787395058, ctime=140723561805927
ccfKYKTZ.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccp4gZwG.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccBLY6kx.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccXptNQZ.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
cc2evs8f.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccJLZfh5.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccdCIvxF.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
cc0gXR4m.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccLAYKJr.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
cc3prXnj.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccGiY326.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
cc5ss2Zi.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccib1twR.res: size=0, mode=100600, atime=1787394974, mtime=1787394974, ctime=140723561805927
ccvf2ZQM.res: size=0, mode=100600, atime=1787394968, mtime=1787394968, ctime=140723561805927
ccYBU297.res: size=0, mode=100600, atime=1787394968, mtime=1787394968, ctime=140723561805927
ccgj0oRU.res: size=0, mode=100600, atime=1787394968, mtime=1787394968, ctime=140723561805927
ccXOz8zo.s: size=412424, mode=100600, atime=1787394087, mtime=1787394088, ctime=140723561805927
ccG8w3Yc.s: size=93022, mode=100600, atime=1787394087, mtime=1787394087, ctime=140723561805927
ccXyyLTB.s: size=414492, mode=100600, atime=1787394087, mtime=1787394087, ctime=140723561805927
cc9iSgNi.s: size=782548, mode=100600, atime=1787394087, mtime=1787394088, ctime=140723561805927
cc9Gr4uY.s: size=412514, mode=100600, atime=1787394087, mtime=1787394087, ctime=140723561805927
ccEYlDul.s: size=93022, mode=100600, atime=1787394004, mtime=1787394004, ctime=140723561805927
ccK00VYL.s: size=414492, mode=100600, atime=1787394004, mtime=1787394004, ctime=140723561805927
ccdMNDP7.s: size=412514, mode=100600, atime=1787394004, mtime=1787394004, ctime=140723561805927
ccgeIEFs.s: size=782548, mode=100600, atime=1787394004, mtime=1787394004, ctime=140723561805927
cclEnBXA.s: size=0, mode=100600, atime=1787394002, mtime=1787394002, ctime=140723561805927
cc6kkPrv.s: size=414166, mode=100600, atime=1787394002, mtime=1787394003, ctime=140723561805927
ccY7SXvo.s: size=782294, mode=100600, atime=1787394002, mtime=1787394003, ctime=140723561805927
cc3ajp8h.s: size=93022, mode=100600, atime=1787394002, mtime=1787394002, ctime=140723561805927
ccmDkQx1.s: size=414492, mode=100600, atime=1787394002, mtime=1787394003, ctime=140723561805927
cc4FxgRJ.s: size=782548, mode=100600, atime=1787394002, mtime=1787394003, ctime=140723561805927
ccKbxKKE.s: size=412514, mode=100600, atime=1787394002, mtime=1787394003, ctime=140723561805927
ccYuOAiN.s: size=782294, mode=100600, atime=1787393982, mtime=1787393983, ctime=140723561805927
ccu2Bbss.s: size=93022, mode=100600, atime=1787393982, mtime=1787393982, ctime=140723561805927
ccJizR48.s: size=414492, mode=100600, atime=1787393982, mtime=1787393982, ctime=140723561805927
ccMhi02y.s: size=782548, mode=100600, atime=1787393982, mtime=1787393983, ctime=140723561805927
cc6oiYJs.s: size=412514, mode=100600, atime=1787393982, mtime=1787393982, ctime=140723561805927
cc53HXtl.s: size=414166, mode=100600, atime=1787393981, mtime=1787393981, ctime=140723561805927
cciGKizl.s: size=782294, mode=100600, atime=1787393981, mtime=1787393982, ctime=140723561805927
cccmH7E5.s: size=414492, mode=100600, atime=1787393981, mtime=1787393981, ctime=140723561805927
ccwtrJGn.s: size=782548, mode=100600, atime=1787393980, mtime=1787393981, ctime=140723561805927
ccLPi8Lq.s: size=412514, mode=100600, atime=1787393980, mtime=1787393981, ctime=140723561805927
cc5v6kGU.s: size=18, mode=100600, atime=1787393624, mtime=1787393624, ctime=140723561805927
ccYpQ87V.s: size=18, mode=100600, atime=1787393623, mtime=1787393623, ctime=140723561805927
ccpOguuF.s: size=18, mode=100600, atime=1787393590, mtime=1787393590, ctime=140723561805927
ccvbTum5.s: size=18, mode=100600, atime=1787393589, mtime=1787393589, ctime=140723561805927
preamble-631c2d.pch: size=4106100, mode=100644, atime=1787403359, mtime=1787393239, ctime=140723561805927
preamble-7a364f.pch: size=4115936, mode=100644, atime=1787407549, mtime=1787393125, ctime=140723561805927
preamble-f5479b.pch: size=289132, mode=100644, atime=1787393107, mtime=1787390209, ctime=140723561805927
preamble-1040f0.pch: size=4781776, mode=100644, atime=1787390077, mtime=1787390077, ctime=140723561805927
preamble-0612cc.pch: size=500408, mode=100644, atime=1787401172, mtime=1787389912, ctime=140723561805927
preamble-82a821.pch: size=4788692, mode=100644, atime=1787389799, mtime=1787389799, ctime=140723561805927
preamble-92376a.pch: size=5212560, mode=100644, atime=1787389741, mtime=1787389741, ctime=140723561805927
preamble-38a825.pch: size=8251588, mode=100644, atime=1787389699, mtime=1787389699, ctime=140723561805927
upload_fileats_HvPMwi: size=80, mode=40700, atime=1787389056, mtime=1787389056, ctime=140723561805927
rpc_metadata_test_WXADU3: size=80, mode=40700, atime=1787389056, mtime=1787389056, ctime=140723561805927
fchownats_test_bgvzdf: size=80, mode=40700, atime=1787389056, mtime=1787389056, ctime=140723561805927
fchmodats_test_69bgPB: size=80, mode=40700, atime=1787389056, mtime=1787389056, ctime=140723561805927
download_fileats_leyhe5: size=80, mode=40700, atime=1787389056, mtime=1787389056, ctime=140723561805927
upload_fileats_VJBR6a: size=80, mode=40700, atime=1787388409, mtime=1787388409, ctime=140723561805927
rpc_metadata_test_ZuxDX5: size=80, mode=40700, atime=1787388409, mtime=1787388409, ctime=140723561805927
fchownats_test_FB9Qdt: size=80, mode=40700, atime=1787388409, mtime=1787388409, ctime=140723561805927
fchmodats_test_QUkdFW: size=80, mode=40700, atime=1787388409, mtime=1787388409, ctime=140723561805927
download_fileats_r3mxtf: size=80, mode=40700, atime=1787388409, mtime=1787388409, ctime=140723561805927
upload_fileats_4ficCM: size=80, mode=40700, atime=1787388317, mtime=1787388317, ctime=140723561805927
fchmodats_test_bLxozk: size=80, mode=40700, atime=1787388317, mtime=1787388317, ctime=140723561805927
fchownats_test_B601wN: size=80, mode=40700, atime=1787388317, mtime=1787388317, ctime=140723561805927
download_fileats_KhULtj: size=80, mode=40700, atime=1787388317, mtime=1787388317, ctime=140723561805927
rpc_metadata_test_FhanLd: size=80, mode=40700, atime=1787388317, mtime=1787388317, ctime=140723561805927
ccKulT19.s: size=2713678, mode=100600, atime=1787388255, mtime=1787388258, ctime=140723561805927
ccaaUyrc.s: size=2136676, mode=100600, atime=1787388255, mtime=1787388257, ctime=140723561805927
cc2xfjPX.s: size=12027813, mode=100600, atime=1787388255, mtime=1787388260, ctime=140723561805927
cc27UhVL.s: size=8624244, mode=100600, atime=1787388255, mtime=1787388259, ctime=140723561805927
ccQ9FeXj.s: size=860901, mode=100600, atime=1787388255, mtime=1787388257, ctime=140723561805927
cc3Dfvm0.s: size=1083206, mode=100600, atime=1787388255, mtime=1787388257, ctime=140723561805927
ccTFymIw.s: size=791570, mode=100600, atime=1787388255, mtime=1787388257, ctime=140723561805927
ccluJNCR.s: size=1121149, mode=100600, atime=1787388255, mtime=1787388256, ctime=140723561805927
ccUzwtSI.s: size=497737, mode=100600, atime=1787388255, mtime=1787388257, ctime=140723561805927
ccoIVmeP.s: size=1599035, mode=100600, atime=1787388255, mtime=1787388258, ctime=140723561805927
ccEYp7Zf.s: size=2390860, mode=100600, atime=1787388255, mtime=1787388258, ctime=140723561805927
ccuv1xEA.s: size=5400541, mode=100600, atime=1787388255, mtime=1787388259, ctime=140723561805927
go-build1431916671: size=60, mode=40700, atime=1787388255, mtime=1787388255, ctime=140723561805927
ccVPtcAJ.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccYEWhpA.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccPuKwNN.s: size=27780, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
cckChTwN.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
cc8mNVmU.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccaRM83y.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccpIjIBd.s: size=23059, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
cct57A6K.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccMJ10Gb.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccBRdg8a.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
ccfM9ecJ.s: size=0, mode=100600, atime=1787388228, mtime=1787388228, ctime=140723561805927
go-build1042492151: size=60, mode=40700, atime=1787388227, mtime=1787388227, ctime=140723561805927
ccbPDinM.res: size=0, mode=100600, atime=1787388136, mtime=1787388136, ctime=140723561805927
ccaIN5Nf.s: size=18, mode=100600, atime=1787388136, mtime=1787388137, ctime=140723561805927
cclhnvX6.s: size=18, mode=100600, atime=1787388136, mtime=1787388136, ctime=140723561805927
ccWIimAS.s: size=24, mode=100600, atime=1787388118, mtime=1787388119, ctime=140723561805927
ccvZ0kpb.s: size=18, mode=100600, atime=1787388118, mtime=1787388119, ctime=140723561805927
ccVgyRT8.s: size=24, mode=100600, atime=1787387966, mtime=1787387966, ctime=140723561805927
ccbsAJAe.s: size=20, mode=100600, atime=1787387966, mtime=1787387966, ctime=140723561805927
ccBXV2kd.s: size=18, mode=100600, atime=1787387966, mtime=1787387966, ctime=140723561805927
ccw3mZQD.s: size=24, mode=100600, atime=1787387966, mtime=1787387966, ctime=140723561805927
preamble-8e7df1.pch: size=4238320, mode=100644, atime=1787401444, mtime=1787386834, ctime=140723561805927
ccpoQ5en.res: size=0, mode=100600, atime=1787386492, mtime=1787386492, ctime=140723561805927
ccVLjMIi.s: size=215472, mode=100600, atime=1787386425, mtime=1787386425, ctime=140723561805927
ccer7RaP.res: size=0, mode=100600, atime=1787386388, mtime=1787386388, ctime=140723561805927
ccdufPYl.s: size=215472, mode=100600, atime=1787386365, mtime=1787386365, ctime=140723561805927
ccokcr4O.s: size=215472, mode=100600, atime=1787386353, mtime=1787386353, ctime=140723561805927
ccHwXUDB.s: size=181159, mode=100600, atime=1787386353, mtime=1787386353, ctime=140723561805927
ccaxFtjV.s: size=15, mode=100600, atime=1787386353, mtime=1787386353, ctime=140723561805927
ccmzWvoK.s: size=15, mode=100600, atime=1787386063, mtime=1787386063, ctime=140723561805927
ccVaaIsJ.s: size=18, mode=100600, atime=1787386063, mtime=1787386063, ctime=140723561805927
cc0LnGgf.s: size=15, mode=100600, atime=1787386063, mtime=1787386063, ctime=140723561805927
ccLcCBiS.s: size=18, mode=100600, atime=1787386014, mtime=1787386014, ctime=140723561805927
ccHgqQzU.s: size=18, mode=100600, atime=1787386014, mtime=1787386014, ctime=140723561805927
ccan7nfz.s: size=25, mode=100600, atime=1787386000, mtime=1787386000, ctime=140723561805927
cc9ofNVG.s: size=18, mode=100600, atime=1787386000, mtime=1787386000, ctime=140723561805927
cceTUEb8.s: size=15, mode=100600, atime=1787386000, mtime=1787386000, ctime=140723561805927
ccLh9waW.s: size=20098, mode=100600, atime=1787386000, mtime=1787386000, ctime=140723561805927
ccAYw1HF.s: size=18, mode=100600, atime=1787386000, mtime=1787386000, ctime=140723561805927
ccw9AvG0.s: size=24, mode=100600, atime=1787386000, mtime=1787386000, ctime=140723561805927
preamble-eb5497.pch: size=4208076, mode=100644, atime=1787385964, mtime=1787385964, ctime=140723561805927
preamble-d7ac98.pch: size=4095484, mode=100644, atime=1787389761, mtime=1787385949, ctime=140723561805927
.ses: size=51, mode=100644, atime=1787384914, mtime=1787384914, ctime=140723561805927
cv_debug.log: size=244, mode=100644, atime=1787384884, mtime=1787405590, ctime=140723561805927
com.microsoft.Edge.jvsrfI: size=80, mode=40700, atime=1787384853, mtime=1787384853, ctime=140723561805927
preamble-36c93e.pch: size=4525316, mode=100644, atime=1787384441, mtime=1787384441, ctime=140723561805927
preamble-4d2a2f.pch: size=4095780, mode=100644, atime=1787384438, mtime=1787384438, ctime=140723561805927
preamble-2c209e.pch: size=4108088, mode=100644, atime=1787384403, mtime=1787384403, ctime=140723561805927
preamble-393248.pch: size=4694164, mode=100644, atime=1787384402, mtime=1787384402, ctime=140723561805927
preamble-cfeaaa.pch: size=4542464, mode=100644, atime=1787384375, mtime=1787384375, ctime=140723561805927
upload_fileats_5Ptlt1: size=80, mode=40700, atime=1787384167, mtime=1787384167, ctime=140723561805927
rpc_metadata_test_FWRSMx: size=80, mode=40700, atime=1787384167, mtime=1787384167, ctime=140723561805927
fchownats_test_ILQiVI: size=80, mode=40700, atime=1787384167, mtime=1787384167, ctime=140723561805927
fchmodats_test_jtJlTe: size=80, mode=40700, atime=1787384167, mtime=1787384167, ctime=140723561805927
download_fileats_dcKCp6: size=80, mode=40700, atime=1787384167, mtime=1787384167, ctime=140723561805927
upload_fileats_dAa6YS: size=80, mode=40700, atime=1787384146, mtime=1787384146, ctime=140723561805927
rpc_metadata_test_IrG6Ku: size=80, mode=40700, atime=1787384146, mtime=1787384146, ctime=140723561805927
fchownats_test_E522aL: size=80, mode=40700, atime=1787384146, mtime=1787384146, ctime=140723561805927
fchmodats_test_j2vdiz: size=80, mode=40700, atime=1787384146, mtime=1787384146, ctime=140723561805927
download_fileats_NrMokE: size=80, mode=40700, atime=1787384146, mtime=1787384146, ctime=140723561805927
preamble-b070e7.pch: size=787736, mode=100644, atime=1787383853, mtime=1787383853, ctime=140723561805927
upload_fileats_yj4TYP: size=80, mode=40700, atime=1787382813, mtime=1787382813, ctime=140723561805927
rpc_metadata_test_mUigyL: size=80, mode=40700, atime=1787382813, mtime=1787382813, ctime=140723561805927
fchownats_test_sU7jM0: size=80, mode=40700, atime=1787382813, mtime=1787382813, ctime=140723561805927
fchmodats_test_1l3Knq: size=80, mode=40700, atime=1787382813, mtime=1787382813, ctime=140723561805927
download_fileats_XXZYd4: size=80, mode=40700, atime=1787382813, mtime=1787382813, ctime=140723561805927
upload_fileats_VnE2Nw: size=80, mode=40700, atime=1787382761, mtime=1787382761, ctime=140723561805927
rpc_metadata_test_09DMV4: size=80, mode=40700, atime=1787382761, mtime=1787382761, ctime=140723561805927
fchownats_test_OVH2UE: size=80, mode=40700, atime=1787382761, mtime=1787382761, ctime=140723561805927
fchmodats_test_9dZei2: size=80, mode=40700, atime=1787382761, mtime=1787382761, ctime=140723561805927
download_fileats_fxVPlA: size=80, mode=40700, atime=1787382761, mtime=1787382761, ctime=140723561805927
upload_fileats_nTLJ9r: size=80, mode=40700, atime=1787382700, mtime=1787382700, ctime=140723561805927
rpc_metadata_test_biU5tu: size=80, mode=40700, atime=1787382700, mtime=1787382700, ctime=140723561805927
fchownats_test_N1U0nH: size=80, mode=40700, atime=1787382700, mtime=1787382700, ctime=140723561805927
fchmodats_test_KdaeGl: size=80, mode=40700, atime=1787382700, mtime=1787382700, ctime=140723561805927
download_fileats_Bjt4YH: size=80, mode=40700, atime=1787382700, mtime=1787382700, ctime=140723561805927
preamble-ca9fc8.pch: size=5275012, mode=100644, atime=1787382478, mtime=1787382478, ctime=140723561805927
t0344-rpc-logs: size=40, mode=40755, atime=1787382145, mtime=1787382145, ctime=140723561805927
upload_fileats_kGfNUy: size=80, mode=40700, atime=1787382040, mtime=1787382040, ctime=140723561805927
rpc_metadata_test_x2sr9y: size=80, mode=40700, atime=1787382040, mtime=1787382040, ctime=140723561805927
fchownats_test_VtS7Ul: size=80, mode=40700, atime=1787382040, mtime=1787382040, ctime=140723561805927
fchmodats_test_gqBMr2: size=80, mode=40700, atime=1787382040, mtime=1787382040, ctime=140723561805927
download_fileats_Enqylt: size=80, mode=40700, atime=1787382040, mtime=1787382040, ctime=140723561805927
upload_fileats_OKv78c: size=80, mode=40700, atime=1787381576, mtime=1787381576, ctime=140723561805927
rpc_metadata_test_BtQFDA: size=80, mode=40700, atime=1787381576, mtime=1787381576, ctime=140723561805927
fchownats_test_qMmCgz: size=80, mode=40700, atime=1787381576, mtime=1787381576, ctime=140723561805927
fchmodats_test_hH6N8A: size=80, mode=40700, atime=1787381576, mtime=1787381576, ctime=140723561805927
download_fileats_QywBF0: size=80, mode=40700, atime=1787381576, mtime=1787381576, ctime=140723561805927
ccnKPIFQ.s: size=18, mode=100600, atime=1787379799, mtime=1787379799, ctime=140723561805927
ccrf6IGv.s: size=10989, mode=100600, atime=1787379799, mtime=1787379799, ctime=140723561805927
preamble-7dbe8b.pch: size=4146592, mode=100644, atime=1787379782, mtime=1787379782, ctime=140723561805927
cckudnvC.s: size=20, mode=100600, atime=1787379735, mtime=1787379735, ctime=140723561805927
preamble-2e1090.pch: size=240544, mode=100644, atime=1787403135, mtime=1787378916, ctime=140723561805927
preamble-5308c7.pch: size=240544, mode=100644, atime=1787389903, mtime=1787378896, ctime=140723561805927
cc7FbgOh.s: size=25, mode=100600, atime=1787378790, mtime=1787378790, ctime=140723561805927
ccQx3Rni.s: size=204227, mode=100600, atime=1787378790, mtime=1787378790, ctime=140723561805927
sm2_ext.cnf: size=144, mode=100644, atime=1787378758, mtime=1787378758, ctime=140723561805927
host_ext.cnf: size=144, mode=100644, atime=1787378747, mtime=1787378747, ctime=140723561805927
ed_host.csr: size=270, mode=100644, atime=1787378747, mtime=1787378747, ctime=140723561805927
ccuMjjNC.s: size=19, mode=100600, atime=1787378164, mtime=1787378164, ctime=140723561805927
ccYqMl6j.s: size=74370, mode=100600, atime=1787376850, mtime=1787376850, ctime=140723561805927
preamble-064318.pch: size=4133140, mode=100644, atime=1787376262, mtime=1787376262, ctime=140723561805927
ccCTmshW.res: size=0, mode=100600, atime=1787374961, mtime=1787374961, ctime=140723561805927
ccEWFmDC.s: size=19, mode=100600, atime=1787374961, mtime=1787374961, ctime=140723561805927
t0312-rdbcomm: size=180, mode=40755, atime=1787373862, mtime=1787373863, ctime=140723561805927
ev351: size=140, mode=40755, atime=1787373800, mtime=1787373863, ctime=140723561805927
rdb-old.log: size=3194, mode=100644, atime=1787373707, mtime=1787373707, ctime=140723561805927
rdb-run.log: size=3194, mode=100644, atime=1787373659, mtime=1787373659, ctime=140723561805927
preamble-4aa6e6.pch: size=4576700, mode=100644, atime=1787373615, mtime=1787373615, ctime=140723561805927
ccrGq2ey.s: size=21, mode=100600, atime=1787373482, mtime=1787373482, ctime=140723561805927
preamble-a5991a.pch: size=4563820, mode=100644, atime=1787373278, mtime=1787373278, ctime=140723561805927
ccHntFVy.s: size=92173, mode=100600, atime=1787372863, mtime=1787372863, ctime=140723561805927
ccNQNJpz.res: size=0, mode=100600, atime=1787372863, mtime=1787372863, ctime=140723561805927
ccA31907.res: size=0, mode=100600, atime=1787372863, mtime=1787372863, ctime=140723561805927
ccZHoHwk.res: size=0, mode=100600, atime=1787372863, mtime=1787372863, ctime=140723561805927
ccNsUAdw.res: size=0, mode=100600, atime=1787372863, mtime=1787372863, ctime=140723561805927
go-build1366321555: size=60, mode=40700, atime=1787372863, mtime=1787372863, ctime=140723561805927
preamble-37874b.pch: size=4095152, mode=100644, atime=1787372702, mtime=1787372702, ctime=140723561805927
preamble-dd32c0.pch: size=4095152, mode=100644, atime=1787372702, mtime=1787372702, ctime=140723561805927
cczOI4jt.s: size=21, mode=100600, atime=1787372688, mtime=1787372688, ctime=140723561805927
cc3ispr5.res: size=0, mode=100600, atime=1787372688, mtime=1787372688, ctime=140723561805927
cchOfBWU.res: size=0, mode=100600, atime=1787372688, mtime=1787372688, ctime=140723561805927
ccWeXrjj.res: size=0, mode=100600, atime=1787372688, mtime=1787372688, ctime=140723561805927
ccgH98wz.res: size=0, mode=100600, atime=1787372688, mtime=1787372688, ctime=140723561805927
go-build2266337521: size=60, mode=40700, atime=1787372687, mtime=1787372688, ctime=140723561805927
cco3FB8u.res: size=0, mode=100600, atime=1787372686, mtime=1787372686, ctime=140723561805927
cctkj7eC.res: size=0, mode=100600, atime=1787372686, mtime=1787372686, ctime=140723561805927
ccJvVbTm.res: size=0, mode=100600, atime=1787372686, mtime=1787372686, ctime=140723561805927
ccno360A.res: size=0, mode=100600, atime=1787372686, mtime=1787372686, ctime=140723561805927
go-build665287256: size=60, mode=40700, atime=1787372686, mtime=1787372686, ctime=140723561805927
ccOxebrm.s: size=21, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
ccr7bKut.res: size=0, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
ccOrYDaK.res: size=0, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
ccBKiTTe.res: size=0, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
cciPC8u5.res: size=0, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
ccVigHJU.res: size=0, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
ccGK9ddp.res: size=0, mode=100600, atime=1787372664, mtime=1787372664, ctime=140723561805927
go-build2691566957: size=60, mode=40700, atime=1787372664, mtime=1787372664, ctime=140723561805927
ccvoM8UA.res: size=0, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
cc8cq1fy.res: size=0, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
cc8gCPUL.res: size=0, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
cch5FZRK.res: size=0, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
cceDQRkq.s: size=21, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
ccw84k2i.res: size=0, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
ccvwP2uH.res: size=0, mode=100600, atime=1787372662, mtime=1787372662, ctime=140723561805927
go-build2744346198: size=60, mode=40700, atime=1787372662, mtime=1787372662, ctime=140723561805927
cc3SyuVz.res: size=0, mode=100600, atime=1787372619, mtime=1787372619, ctime=140723561805927
ccWQPIus.res: size=0, mode=100600, atime=1787372618, mtime=1787372618, ctime=140723561805927
ccgr3Qmv.s: size=21, mode=100600, atime=1787372618, mtime=1787372619, ctime=140723561805927
ccz2Lxck.s: size=21, mode=100600, atime=1787372618, mtime=1787372619, ctime=140723561805927
ccRpD5mF.res: size=0, mode=100600, atime=1787372618, mtime=1787372618, ctime=140723561805927
ccIwg7Mk.res: size=0, mode=100600, atime=1787372618, mtime=1787372618, ctime=140723561805927
cc1EbPsO.s: size=21, mode=100600, atime=1787372618, mtime=1787372619, ctime=140723561805927
ccEJhEKy.s: size=21, mode=100600, atime=1787372618, mtime=1787372619, ctime=140723561805927
cc81dCKJ.s: size=21, mode=100600, atime=1787372618, mtime=1787372619, ctime=140723561805927
go-build2277048978: size=60, mode=40700, atime=1787372618, mtime=1787372618, ctime=140723561805927
ccHja3Eg.s: size=207516, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
ccrmYB4Z.s: size=427, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
ccmvSnTu.s: size=173669, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
cchc9eZY.s: size=21, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
go-build1999408651: size=40, mode=40700, atime=1787372617, mtime=1787372617, ctime=140723561805927
cccAPePH.res: size=0, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
cco1Ulnx.o: size=1256, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
ccPuhPij.s: size=427, mode=100600, atime=1787372617, mtime=1787372617, ctime=140723561805927
ccqiEVtZ.s: size=21, mode=100600, atime=1787372616, mtime=1787372617, ctime=140723561805927
ccCx7Jib.s: size=21, mode=100600, atime=1787372616, mtime=1787372617, ctime=140723561805927
cc07fn5X.s: size=21, mode=100600, atime=1787372616, mtime=1787372617, ctime=140723561805927
cc2OT30y.s: size=21, mode=100600, atime=1787372616, mtime=1787372617, ctime=140723561805927
ccGwUMew.s: size=207528, mode=100600, atime=1787372616, mtime=1787372617, ctime=140723561805927
cc5yzGJP.s: size=182249, mode=100600, atime=1787372616, mtime=1787372617, ctime=140723561805927
go-build3686139062: size=60, mode=40700, atime=1787372616, mtime=1787372616, ctime=140723561805927
ev350: size=80, mode=40755, atime=1787371805, mtime=1787371847, ctime=140723561805927
rpc_daemon.pid: size=6, mode=100640, atime=1787371539, mtime=1787371539, ctime=140723561805927
upload_fileats_P94aXw: size=80, mode=40700, atime=1787371490, mtime=1787371490, ctime=140723561805927
rpc_metadata_test_oHaIU0: size=80, mode=40700, atime=1787371490, mtime=1787371490, ctime=140723561805927
fchownats_test_va9oty: size=80, mode=40700, atime=1787371490, mtime=1787371490, ctime=140723561805927
fchmodats_test_1Gbanw: size=80, mode=40700, atime=1787371490, mtime=1787371490, ctime=140723561805927
download_fileats_mcnAmK: size=80, mode=40700, atime=1787371490, mtime=1787371490, ctime=140723561805927
ev349: size=80, mode=40755, atime=1787371198, mtime=1787371200, ctime=140723561805927
t0349-r4.log: size=5101, mode=100644, atime=1787371147, mtime=1787371147, ctime=140723561805927
t0349-r3.log: size=2629, mode=100644, atime=1787371091, mtime=1787371091, ctime=140723561805927
t0349-r2.log: size=2629, mode=100644, atime=1787370992, mtime=1787370936, ctime=140723561805927
t0349-run.log: size=2629, mode=100644, atime=1787370936, mtime=1787370828, ctime=140723561805927
t0312-r4.log: size=3479, mode=100644, atime=1787369113, mtime=1787369113, ctime=140723561805927
t0312-r3.log: size=3319, mode=100644, atime=1787369034, mtime=1787369034, ctime=140723561805927
t0312-run2.log: size=3319, mode=100644, atime=1787368856, mtime=1787368856, ctime=140723561805927
t0312-run.log: size=3319, mode=100644, atime=1787368855, mtime=1787368763, ctime=140723561805927
upload_fileats_sVffkF: size=80, mode=40700, atime=1787368261, mtime=1787368261, ctime=140723561805927
rpc_metadata_test_ZkAkLv: size=80, mode=40700, atime=1787368261, mtime=1787368261, ctime=140723561805927
fchownats_test_wrko4I: size=80, mode=40700, atime=1787368261, mtime=1787368261, ctime=140723561805927
fchmodats_test_V7sXv8: size=80, mode=40700, atime=1787368261, mtime=1787368261, ctime=140723561805927
download_fileats_NU59fx: size=80, mode=40700, atime=1787368261, mtime=1787368261, ctime=140723561805927
rdbcomm-tool-test-17611: size=60, mode=40755, atime=1787368224, mtime=1787368224, ctime=140723561805927
rdbcomm-tool-test-17610: size=60, mode=40755, atime=1787368223, mtime=1787368223, ctime=140723561805927
upload_fileats_M0gAtF: size=80, mode=40700, atime=1787368223, mtime=1787368223, ctime=140723561805927
obt: size=60, mode=40755, atime=1787368223, mtime=1787368223, ctime=140723561805927
cv_debug.log.tmp: size=9, mode=100644, atime=1787368223, mtime=1787410176, ctime=140723561805927
preamble-6376a5.pch: size=9, mode=100644, atime=1787410176, mtime=1787410176, ctime=140723561805927
pread_test_src.bin: size=29, mode=100644, atime=1787410176, mtime=1787410176, ctime=140723561805927
rpc_metadata_test_xjA1Tn: size=80, mode=40700, atime=1787368223, mtime=1787368223, ctime=140723561805927
logger_test.audit.log: size=3610, mode=100644, atime=1787410176, mtime=1787410176, ctime=140723561805927
test_logger.log: size=0, mode=100644, atime=1787368223, mtime=1787368223, ctime=140723561805927
fchownats_test_fzVhRb: size=80, mode=40700, atime=1787368223, mtime=1787368223, ctime=140723561805927
fchmodats_test_caEIrh: size=80, mode=40700, atime=1787368223, mtime=1787368223, ctime=140723561805927
aio: size=60, mode=40755, atime=1787368223, mtime=1787368223, ctime=140723561805927
test_file_3.bin: size=6, mode=100644, atime=1787368223, mtime=1787410176, ctime=140723561805927
download_fileats_6r5Mvb: size=80, mode=40700, atime=1787368223, mtime=1787368223, ctime=140723561805927
tmp2: size=60, mode=40755, atime=1787368223, mtime=1787368223, ctime=140723561805927
cc4phy5E.s: size=29, mode=100644, atime=1787410176, mtime=1787410176, ctime=140723561805927
rpc_dir_tree_test: size=100, mode=40755, atime=1787410176, mtime=1787368223, ctime=140723561805927
tmp1: size=140, mode=40755, atime=1787368223, mtime=1787410176, ctime=140723561805927
evidence_placeholder: size=7, mode=100644, atime=1787367909, mtime=1787367909, ctime=140723561805927
ev346: size=100, mode=40755, atime=1787367898, mtime=1787367909, ctime=140723561805927
tls-stress-5.out: size=22, mode=100644, atime=1787367122, mtime=1787367170, ctime=140723561805927
tls-stress-4.out: size=22, mode=100644, atime=1787367118, mtime=1787367168, ctime=140723561805927
tls-stress-3.out: size=22, mode=100644, atime=1787367116, mtime=1787367165, ctime=140723561805927
tls-stress-2.out: size=0, mode=100644, atime=1787367175, mtime=1787367173, ctime=140723561805927
tls-stress-1.out: size=22, mode=100644, atime=1787367111, mtime=1787367173, ctime=140723561805927
t0346-p: size=60, mode=40755, atime=1787365900, mtime=1787365900, ctime=140723561805927
t0346-r: size=60, mode=40755, atime=1787365896, mtime=1787365896, ctime=140723561805927
t0346-final2.sh: size=1208, mode=100755, atime=1787365903, mtime=1787365895, ctime=140723561805927
t0344-client-new: size=100, mode=40755, atime=1787365871, mtime=1787365871, ctime=140723561805927
t0346-regression.sh: size=1154, mode=100755, atime=1787365795, mtime=1787365689, ctime=140723561805927
t0346-f: size=60, mode=40755, atime=1787365661, mtime=1787365661, ctime=140723561805927
t0346-final.sh: size=570, mode=100755, atime=1787365664, mtime=1787365660, ctime=140723561805927
t0346-m: size=60, mode=40755, atime=1787365459, mtime=1787365459, ctime=140723561805927
t0346-verify2.sh: size=715, mode=100755, atime=1787365463, mtime=1787365429, ctime=140723561805927
t0346-certs: size=300, mode=40755, atime=1787365739, mtime=1787365786, ctime=140723561805927
t0346-verify.sh: size=709, mode=100755, atime=1787365375, mtime=1787365370, ctime=140723561805927
conv_v3.json: size=269, mode=100644, atime=1787364801, mtime=1787364801, ctime=140723561805927
evidence-t0344: size=100, mode=40755, atime=1787364747, mtime=1787364782, ctime=140723561805927
t0344-mA: size=60, mode=40755, atime=1787364509, mtime=1787364509, ctime=140723561805927
t0344-ac5f.sh: size=743, mode=100755, atime=1787364513, mtime=1787364457, ctime=140723561805927
t0344-m9: size=60, mode=40755, atime=1787364337, mtime=1787364337, ctime=140723561805927
t0344-ac5e.sh: size=457, mode=100755, atime=1787364339, mtime=1787364337, ctime=140723561805927
t0344-m8: size=60, mode=40755, atime=1787364308, mtime=1787364308, ctime=140723561805927
t0344-ac5d.sh: size=672, mode=100755, atime=1787364312, mtime=1787364308, ctime=140723561805927
t0344-client.strace: size=351, mode=100644, atime=1787364133, mtime=1787364133, ctime=140723561805927
t0344-client-out.log: size=0, mode=100644, atime=1787364133, mtime=1787364133, ctime=140723561805927
t0344-s9.log: size=539, mode=100644, atime=1787364130, mtime=1787364133, ctime=140723561805927
t0344-m7: size=60, mode=40755, atime=1787364154, mtime=1787364130, ctime=140723561805927
t0344-ac5c.sh: size=805, mode=100755, atime=1787364133, mtime=1787364130, ctime=140723561805927
t0344-s8.log: size=539, mode=100644, atime=1787364087, mtime=1787364086, ctime=140723561805927
t0344-m6: size=60, mode=40755, atime=1787364083, mtime=1787364083, ctime=140723561805927
t0344-ac5b.sh: size=616, mode=100755, atime=1787364087, mtime=1787364083, ctime=140723561805927
t0344-s7.log: size=539, mode=100644, atime=1787364004, mtime=1787364003, ctime=140723561805927
t0344-m5: size=60, mode=40755, atime=1787364000, mtime=1787364000, ctime=140723561805927
t0344-ac5.sh: size=728, mode=100755, atime=1787364004, mtime=1787364000, ctime=140723561805927
t0344-s6.log: size=544, mode=100644, atime=1787363863, mtime=1787363866, ctime=140723561805927
t0344-s5.log: size=544, mode=100644, atime=1787363843, mtime=1787363812, ctime=140723561805927
t0344-manual2: size=60, mode=40755, atime=1787363809, mtime=1787363809, ctime=140723561805927
t0344-full2.log: size=4498, mode=100644, atime=1787363604, mtime=1787363555, ctime=140723561805927
t0344-full.log: size=2222, mode=100644, atime=1787363453, mtime=1787363453, ctime=140723561805927
t0344-server.log: size=543, mode=100644, atime=1787363259, mtime=1787363259, ctime=140723561805927
t0344-manual: size=60, mode=40755, atime=1787363256, mtime=1787363256, ctime=140723561805927
preamble-97ca5e.pch: size=818472, mode=100644, atime=1787369068, mtime=1787362549, ctime=140723561805927
preamble-20b12f.pch: size=5133084, mode=100644, atime=1787362127, mtime=1787362127, ctime=140723561805927
preamble-c3c5e4.pch: size=8188176, mode=100644, atime=1787361442, mtime=1787361442, ctime=140723561805927
preamble-af70b8.pch: size=5007456, mode=100644, atime=1787361327, mtime=1787361327, ctime=140723561805927
backupstream-resource-lock-Jdm0yG: size=160, mode=40700, atime=1787361020, mtime=1787361020, ctime=140723561805927
backupstream-catalog-c-api-9qSa7z-shm: size=32768, mode=100644, atime=1787361020, mtime=1787361020, ctime=140723561805927
backupstream-catalog-c-api-9qSa7z-wal: size=0, mode=100644, atime=1787361020, mtime=1787361020, ctime=140723561805927
backupstream-resource-lock-0f4CkI: size=160, mode=40700, atime=1787360815, mtime=1787360815, ctime=140723561805927
backupstream-catalog-c-api-otIW9U-shm: size=32768, mode=100644, atime=1787360815, mtime=1787360815, ctime=140723561805927
backupstream-catalog-c-api-otIW9U-wal: size=0, mode=100644, atime=1787360815, mtime=1787360815, ctime=140723561805927
preamble-91370d.pch: size=5161600, mode=100644, atime=1787360715, mtime=1787360715, ctime=140723561805927
new_conv.json: size=250, mode=100644, atime=1787360648, mtime=1787360648, ctime=140723561805927
evidence-rpc: size=100, mode=40755, atime=1787360620, mtime=1787360620, ctime=140723561805927
backupstream-resource-lock-zkr0lG: size=160, mode=40700, atime=1787360536, mtime=1787360536, ctime=140723561805927
backupstream-catalog-c-api-VEGZR4-shm: size=32768, mode=100644, atime=1787360536, mtime=1787360536, ctime=140723561805927
backupstream-catalog-c-api-VEGZR4-wal: size=0, mode=100644, atime=1787360536, mtime=1787360536, ctime=140723561805927
backupstream-resource-lock-d1insK: size=160, mode=40700, atime=1787360390, mtime=1787360390, ctime=140723561805927
backupstream-catalog-c-api-mPlYQw-shm: size=32768, mode=100644, atime=1787360389, mtime=1787360389, ctime=140723561805927
backupstream-catalog-c-api-mPlYQw-wal: size=0, mode=100644, atime=1787360389, mtime=1787360389, ctime=140723561805927
tls_test_new_cLxQmE: size=40, mode=40700, atime=1787360354, mtime=1787360354, ctime=140723561805927
tls_test_old_Xp2lJo: size=140, mode=40700, atime=1787360354, mtime=1787360354, ctime=140723561805927
tls_test_new_3zTuf8: size=40, mode=40700, atime=1787360340, mtime=1787360340, ctime=140723561805927
tls_test_old_tHRdc0: size=140, mode=40700, atime=1787360354, mtime=1787360340, ctime=140723561805927
test_build.sh: size=322, mode=100755, atime=1787360297, mtime=1787360297, ctime=140723561805927
new_impl.md: size=2644, mode=100644, atime=1787360202, mtime=1787360202, ctime=140723561805927
full_output.log: size=710, mode=100644, atime=1787359847, mtime=1787359837, ctime=140723561805927
preamble-33ac35.pch: size=4637928, mode=100644, atime=1787360107, mtime=1787359798, ctime=140723561805927
tls_test_new_oWR10f: size=40, mode=40700, atime=1787359486, mtime=1787359486, ctime=140723561805927
tls_test_old_pGTjJ1: size=140, mode=40700, atime=1787359486, mtime=1787359486, ctime=140723561805927
preamble-a9900e.pch: size=245180, mode=100644, atime=1787370685, mtime=1787358901, ctime=140723561805927
preamble-9b89b3.pch: size=4566512, mode=100644, atime=1787358759, mtime=1787358759, ctime=140723561805927
inject2.py: size=723, mode=100644, atime=1787357887, mtime=1787357887, ctime=140723561805927
backupstream-resource-lock-5AcLMb: size=160, mode=40700, atime=1787357801, mtime=1787357801, ctime=140723561805927
backupstream-catalog-c-api-94Khxh-shm: size=32768, mode=100644, atime=1787357800, mtime=1787357800, ctime=140723561805927
backupstream-catalog-c-api-94Khxh-wal: size=0, mode=100644, atime=1787357800, mtime=1787357800, ctime=140723561805927
tls_test_new_2iKHlU: size=40, mode=40700, atime=1787357453, mtime=1787357453, ctime=140723561805927
tls_test_old_hBuROu: size=140, mode=40700, atime=1787357453, mtime=1787357453, ctime=140723561805927
preamble-c3537b.pch: size=4763000, mode=100644, atime=1787360366, mtime=1787357441, ctime=140723561805927
preamble-953bb4.pch: size=4643300, mode=100644, atime=1787357430, mtime=1787357400, ctime=140723561805927
backupstream-resource-lock-wqFyib: size=160, mode=40700, atime=1787357253, mtime=1787357253, ctime=140723561805927
backupstream-catalog-c-api-M3pClR-shm: size=32768, mode=100644, atime=1787357252, mtime=1787357252, ctime=140723561805927
backupstream-catalog-c-api-M3pClR-wal: size=0, mode=100644, atime=1787357252, mtime=1787357252, ctime=140723561805927
backupstream-resource-lock-0fTi51: size=160, mode=40700, atime=1787357184, mtime=1787357184, ctime=140723561805927
backupstream-catalog-c-api-FD0lrD-shm: size=32768, mode=100644, atime=1787357183, mtime=1787357183, ctime=140723561805927
backupstream-catalog-c-api-FD0lrD-wal: size=0, mode=100644, atime=1787357183, mtime=1787357183, ctime=140723561805927
grill_qa.jsonl: size=978, mode=100644, atime=1787357076, mtime=1787357076, ctime=140723561805927
tls_test_new_ejMX20: size=40, mode=40700, atime=1787356896, mtime=1787356896, ctime=140723561805927
tls_test_old_hxuQ8r: size=120, mode=40700, atime=1787356896, mtime=1787356896, ctime=140723561805927
test_load: size=16592, mode=100755, atime=1787356855, mtime=1787356855, ctime=140723561805927
test_load.c: size=1158, mode=100644, atime=1787356855, mtime=1787356855, ctime=140723561805927
host_key_pub.pem: size=113, mode=100644, atime=1787356847, mtime=1787356847, ctime=140723561805927
host_pub.pem: size=113, mode=100644, atime=1787356847, mtime=1787356847, ctime=140723561805927
tls_test_new_o3wotR: size=40, mode=40700, atime=1787356828, mtime=1787356828, ctime=140723561805927
tls_test_old_DDq2H1: size=120, mode=40700, atime=1787356828, mtime=1787356828, ctime=140723561805927
preamble-1abcd4.pch: size=5070184, mode=100644, atime=1787356739, mtime=1787356732, ctime=140723561805927
gen_sm2_client: size=100, mode=40755, atime=1787356630, mtime=1787356630, ctime=140723561805927
certs_backup: size=360, mode=40755, atime=1787356621, mtime=1787356621, ctime=140723561805927
gen_sm2: size=140, mode=40755, atime=1787356610, mtime=1787356610, ctime=140723561805927
gen_ed25519: size=140, mode=40755, atime=1787356605, mtime=1787356605, ctime=140723561805927
convergence_v2.json: size=299, mode=100644, atime=1787356369, mtime=1787356369, ctime=140723561805927
new_convergence.json: size=299, mode=100644, atime=1787356364, mtime=1787356364, ctime=140723561805927
rpc_hs_tmp_84o17i: size=220, mode=40700, atime=1787356326, mtime=1787356326, ctime=140723561805927
review_report.md: size=1972, mode=100644, atime=1787356027, mtime=1787356004, ctime=140723561805927
old_test.log: size=556, mode=100644, atime=1787355985, mtime=1787355985, ctime=140723561805927
out_5.log: size=696, mode=100644, atime=1787355970, mtime=1787355970, ctime=140723561805927
out_4.log: size=696, mode=100644, atime=1787355970, mtime=1787355970, ctime=140723561805927
out_3.log: size=696, mode=100644, atime=1787355970, mtime=1787355970, ctime=140723561805927
out_2.log: size=696, mode=100644, atime=1787355970, mtime=1787355970, ctime=140723561805927
out_1.log: size=696, mode=100644, atime=1787355970, mtime=1787355970, ctime=140723561805927
evidence: size=140, mode=40755, atime=1787356017, mtime=1787356357, ctime=140723561805927
tmp.Fy4287R7m2: size=80, mode=40700, atime=1787355794, mtime=1787355794, ctime=140723561805927
tls_cli_5o44yk: size=100, mode=40700, atime=1787355776, mtime=1787355776, ctime=140723561805927
tls_test_new_RUdhrQ: size=40, mode=40700, atime=1787355711, mtime=1787355711, ctime=140723561805927
tls_test_old_Bl0uZW: size=120, mode=40700, atime=1787355711, mtime=1787355711, ctime=140723561805927
backupstream-resource-lock-fmtRBH: size=160, mode=40700, atime=1787355696, mtime=1787355696, ctime=140723561805927
backupstream-catalog-c-api-fCmLhB-shm: size=32768, mode=100644, atime=1787355696, mtime=1787355696, ctime=140723561805927
backupstream-catalog-c-api-fCmLhB-wal: size=0, mode=100644, atime=1787355696, mtime=1787355696, ctime=140723561805927
ccEHwA3d.s: size=4661100, mode=100600, atime=1787355667, mtime=1787355672, ctime=140723561805927
ccyTSWcG.s: size=945676, mode=100600, atime=1787355667, mtime=1787355670, ctime=140723561805927
ccMcEXdD.s: size=128341, mode=100600, atime=1787355667, mtime=1787355668, ctime=140723561805927
ccZ57uSC.s: size=1850602, mode=100600, atime=1787355667, mtime=1787355671, ctime=140723561805927
ccogNAIs.s: size=1423945, mode=100600, atime=1787355667, mtime=1787355670, ctime=140723561805927
ccaHnxkz.s: size=550322, mode=100600, atime=1787355667, mtime=1787355669, ctime=140723561805927
ccytJAHD.s: size=945676, mode=100600, atime=1787355667, mtime=1787355669, ctime=140723561805927
ccZneLi5.s: size=3448151, mode=100600, atime=1787355667, mtime=1787355672, ctime=140723561805927
ccgecEnM.s: size=5116486, mode=100600, atime=1787355667, mtime=1787355672, ctime=140723561805927
ccGrGzBL.s: size=3448151, mode=100600, atime=1787355667, mtime=1787355671, ctime=140723561805927
ccmgQOC8.s: size=225800, mode=100600, atime=1787355667, mtime=1787355669, ctime=140723561805927
ccQSgcUa.s: size=1296004, mode=100600, atime=1787355667, mtime=1787355670, ctime=140723561805927
ccLXdvov.s: size=1850602, mode=100600, atime=1787355667, mtime=1787355671, ctime=140723561805927
cc3GOYYr.s: size=1296004, mode=100600, atime=1787355667, mtime=1787355669, ctime=140723561805927
ccQws9dU.s: size=1446951, mode=100600, atime=1787355667, mtime=1787355669, ctime=140723561805927
cc90PlJI.s: size=1502537, mode=100600, atime=1787355667, mtime=1787355669, ctime=140723561805927
ccw5oea5.s: size=128580, mode=100600, atime=1787355667, mtime=1787355668, ctime=140723561805927
ccQG99bN.s: size=1858901, mode=100600, atime=1787355666, mtime=1787355669, ctime=140723561805927
cc0GwGuz.s: size=1431374, mode=100600, atime=1787355666, mtime=1787355670, ctime=140723561805927
ccIA8Co4.s: size=550803, mode=100600, atime=1787355666, mtime=1787355667, ctime=140723561805927
ccJhzGKv.s: size=3448767, mode=100600, atime=1787355666, mtime=1787355671, ctime=140723561805927
ccpCMnaR.s: size=946580, mode=100600, atime=1787355666, mtime=1787355668, ctime=140723561805927
ccTInkNy.s: size=5117257, mode=100600, atime=1787355666, mtime=1787355672, ctime=140723561805927
cceOZ3Qw.s: size=3448767, mode=100600, atime=1787355666, mtime=1787355671, ctime=140723561805927
cc8bLdAS.s: size=225901, mode=100600, atime=1787355667, mtime=1787355667, ctime=140723561805927
ccJqlPaS.s: size=1296197, mode=100600, atime=1787355666, mtime=1787355668, ctime=140723561805927
ccBojA8N.s: size=4662977, mode=100600, atime=1787355666, mtime=1787355671, ctime=140723561805927
ccu9Vgdh.s: size=1858901, mode=100600, atime=1787355666, mtime=1787355670, ctime=140723561805927
ccIpThza.s: size=1450853, mode=100600, atime=1787355666, mtime=1787355668, ctime=140723561805927
ccjWNufF.s: size=1296197, mode=100600, atime=1787355666, mtime=1787355667, ctime=140723561805927
ccKJLDIk.s: size=946580, mode=100600, atime=1787355666, mtime=1787355668, ctime=140723561805927
ccnkBtEh.s: size=1505974, mode=100600, atime=1787355666, mtime=1787355668, ctime=140723561805927
new_test.c: size=14988, mode=100644, atime=1787355543, mtime=1787355538, ctime=140723561805927
tmp.Q436rAB5v3: size=80, mode=40700, atime=1787355236, mtime=1787355236, ctime=140723561805927
tmp.4db1tGJqOG: size=80, mode=40700, atime=1787355194, mtime=1787355194, ctime=140723561805927
backupstream-test-port-locks-1000: size=42840, mode=40755, atime=1787355040, mtime=1787367173, ctime=140723561805927
backupstream-resource-lock-QxWaPE: size=160, mode=40700, atime=1787355040, mtime=1787355040, ctime=140723561805927
backupstream-catalog-c-api-Bw5Ooi-shm: size=32768, mode=100644, atime=1787355039, mtime=1787355039, ctime=140723561805927
backupstream-catalog-c-api-Bw5Ooi-wal: size=0, mode=100644, atime=1787355039, mtime=1787355039, ctime=140723561805927
preamble-5b10c0.pch: size=4313852, mode=100644, atime=1787357393, mtime=1787354288, ctime=140723561805927
review.py: size=888, mode=100644, atime=1787354068, mtime=1787354068, ctime=140723561805927
inject.py: size=1223, mode=100644, atime=1787354022, mtime=1787354022, ctime=140723561805927
preamble-c1266e.pch: size=240680, mode=100644, atime=1787355487, mtime=1787353845, ctime=140723561805927
preamble-16c946.pch: size=2460076, mode=100644, atime=1787353842, mtime=1787353842, ctime=140723561805927
test_new2.c: size=1778, mode=100644, atime=1787353822, mtime=1787353822, ctime=140723561805927
test_new_api.c: size=2292, mode=100644, atime=1787353813, mtime=1787353807, ctime=140723561805927
pdca-task-identity-0e73a54cf0ba2a78f24936698bf7dd779208d391ff9365e8cd89af4a61658101.lock: size=0, mode=100600, atime=1787352553, mtime=1787352553, ctime=140723561805927
preamble-c4a8b7.pch: size=2217140, mode=100644, atime=1787352490, mtime=1787352490, ctime=140723561805927
.bun-1000-71b650bef1b3e52c.node: size=514960, mode=100600, atime=1787353719, mtime=1787352267, ctime=140723561805927
.bun-1000-ce78de25a2553a8.so: size=5576816, mode=100600, atime=1787353719, mtime=1787352267, ctime=140723561805927
node-compile-cache: size=60, mode=40755, atime=1787352265, mtime=1787352265, ctime=140723561805927
.bun-1000-73b412e2ff3bc470.so: size=13745312, mode=100600, atime=1787353715, mtime=1787352263, ctime=140723561805927
opencode: size=3200, mode=40755, atime=1787387255, mtime=1787394920, ctime=140723561805927
.xmake1000: size=60, mode=40755, atime=1787352182, mtime=1787352182, ctime=140723561805927
systemd-private-f4242d5c2011421fa073c1d11beb8ddc-upower.service-qW6oMT: size=60, mode=40700, atime=1787351773, mtime=1787351773, ctime=140723561805927
tmux-1000: size=60, mode=40700, atime=1787351766, mtime=1787351766, ctime=140723561805927
FlClashSocket_272.sock: size=0, mode=140755, atime=1787351600, mtime=1787351600, ctime=140723561805927
systemd-private-f4242d5c2011421fa073c1d11beb8ddc-power-profiles-daemon.service-lOiCEt: size=60, mode=40700, atime=1787351600, mtime=1787351600, ctime=140723561805927
systemd-private-f4242d5c2011421fa073c1d11beb8ddc-polkit.service-sVAxgU: size=60, mode=40700, atime=1787351598, mtime=1787351598, ctime=140723561805927
.X1-lock: size=11, mode=100444, atime=1787351598, mtime=1787351598, ctime=140723561805927
sddm-:0-RdTTxP: size=0, mode=140700, atime=1787351592, mtime=1787351592, ctime=140723561805927
sddm-auth-98a4d6ad-ec9d-47f0-a96c-6aa5b06e3631: size=0, mode=140755, atime=1787351596, mtime=1787351591, ctime=140723561805927
systemd-private-f4242d5c2011421fa073c1d11beb8ddc-systemd-logind.service-YKZpne: size=60, mode=40700, atime=1787351590, mtime=1787351590, ctime=140723561805927
systemd-private-f4242d5c2011421fa073c1d11beb8ddc-iwd.service-JvqLbp: size=60, mode=40700, atime=1787351590, mtime=1787351590, ctime=140723561805927
systemd-private-f4242d5c2011421fa073c1d11beb8ddc-bluetooth.service-G6YCLw: size=60, mode=40700, atime=1787351590, mtime=1787351590, ctime=140723561805927
.font-unix: size=40, mode=41777, atime=1787351590, mtime=1787351590, ctime=140723561805927
.XIM-unix: size=40, mode=41777, atime=1787351590, mtime=1787351590, ctime=140723561805927
.ICE-unix: size=40, mode=41777, atime=1787351590, mtime=1787351590, ctime=140723561805927
.X11-unix: size=80, mode=41777, atime=1787351590, mtime=1787351598, ctime=140723561805927
[0m[38;2;0;255;0;1m[ 50%]:[0m running.test symlink/default[0m
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140252424266624| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
rpc_net_time_test: PASS
[0m[38;2;0;255;0;1m[ 52%]:[0m running.test tls_cert_test/default[0m
PASS

=== TEST: TYPE_UPDATE - Large Data Write ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_10
[0m[38;2;0;255;0;1m[ 55%]:[0m running.test upload_fileats/default[0m
[PASS] handshake codec
[PASS] handshake_resp codec
[PASS] algorithm mapping
[PASS] plain both disabled
[PASS] server mTLS reject plain
[2026-08-22 22:49:36]|Error|rpc/rpc-io.cpp:133 rpc_handshake_client_negotiate|139722730689408| handshake: server downgraded to plain but mTLS requested, abort
[PASS] client mtls rejected downgrade to plain
rpc_own_handshake_test: ALL PASS
========================================
  rpc_conn_cli_readdir_tree 集成测试
========================================

=== Test 1: basic tree traversal ===
  OK: 6 entries returned

=== Test 2: stat metadata ===
  OK: file types and sizes

=== Test 3: empty directory ===
  OK: empty dir returns 0 entries

========================================
  ALL TESTS PASSED
[PASS] rdb algorithm exact mapping
[PASS] plain zero-handshake passthrough
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140252424266624| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
PASS

=== TEST: TYPE_UPDATE - Large Data Write Overwrite Partial ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_25
[2026-08-22 22:49:36]|Info|rpc/rpc.cpp:2959 rpc_conn_cli_upload_fileats|140317764351680| upload_fileat /tmp/upload_fileats_vLZjyD/dst/:test1.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc.cpp:2959 rpc_conn_cli_upload_fileats|140317764351680| upload_fileat /tmp/upload_fileats_vLZjyD/dst/:test2.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4010 rpc_conn_srv_upload_fileats|140317755958976| openat test1.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4033 rpc_conn_srv_upload_fileats|140317755958976| upload_fileat /tmp/upload_fileats_vLZjyD/dst/:test1.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4010 rpc_conn_srv_upload_fileats|140317755958976| openat test2.txt success.
[2026-08-22 22:49:36]|Info|rpc/rpc-server.cpp:4033 rpc_conn_srv_upload_fileats|140317755958976| upload_fileat /tmp/upload_fileats_vLZjyD/dst/:test2.txt success.
AC-2 mixed on-demand mTLS PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_SM4_GCM_SM3
=== TLS Cert Unit Tests ===

Using CERT_DIR: /home/black/Public/aio/aio-tools/6200/F/139/libs/tests/certs
Running tls_cert_build_server_profiles... PASSED
Running tls_cert_build_client_profile... PASSED
Running tls_cert_init_server_from_cert_dir... [2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_SM4_GCM_SM3
PASS

=== TEST: TYPE_UPDATE - 1M File Overwrite Single Write ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_26
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
AC-2 mixed on-demand mTLS PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
PASS

=== TEST: BOUNDARY - Max Block Size 16K ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_09
PASSED
Running tls_cert_init_client_from_cert_dir... [2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[2026-08-22 22:49:36]|Error|libs/tls_cert.c:75 tls_cert_log_setup_error|139784180487040| TLS setup failed: role=client stage=ca-certificate algorithm=TLS_AES_256_GCM_SHA384 ca=/nonexistent/ed25519_ca.crt cert=/nonexistent/my-ca/host.crt key=/nonexistent/my-ca/host.key
PASSED
Running tls_cert_init_disabled... PASSED
Running tls_ed25519_dual_format... [2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_SM4_GCM_SM3
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_SM4_GCM_SM3
PASS

=== TEST: BOUNDARY - Max Block Size 64K ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_10
[PASS] on-demand mTLS upgrade
[PASS] reject without downgrade
rdbcomm_handshake_session_test: ALL PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
PASS

=== TEST: TRUNCATE ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_11
PASSED
Running tls_server_init... [2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_SM4_GCM_SM3
AC-3 forced mTLS PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_SM4_GCM_SM3
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
PASSED
Running tls_mtls_handshake... [2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_SM4_GCM_SM3
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
AC-3 forced mTLS PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[2026-08-22 22:49:36]|Error|libs/tls_cert.c:75 tls_cert_log_setup_error|140032500388736| TLS setup failed: role=client stage=ca-certificate algorithm=TLS_AES_256_GCM_SHA384 ca=/tmp/t0352-missing-certs/ed25519_ca.crt cert=/tmp/t0352-missing-certs/ED25519_Test_CA/host.crt key=/tmp/t0352-missing-certs/ED25519_Test_CA/host.key
[2026-08-22 22:49:36]|Error|rpc/rpc-io.cpp:154 rpc_handshake_client_negotiate|140032500388736| handshake: tls_cert_init_client failed: cert_dir=/tmp/t0352-missing-certs algorithm=TLS_AES_256_GCM_SHA384 ca_cn=ED25519_Test_CA
[2026-08-22 22:49:36]|Error|libs/tls_cert.c:62 tls_cert_log_ssl_errors|140032500388736| TLS handshake failed: role=server stage=handshake ssl_error=1
[2026-08-22 22:49:36]|Error|libs/tls_cert.c:66 tls_cert_log_ssl_errors|140032500388736| TLS OpenSSL error: error:0A000126:SSL routines::unexpected eof while reading
PASS

=== TEST: CURSOR REUSE ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_12
AC-4 missing client cert_dir fail PASS
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_SM4_GCM_SM3
PASS

=== TEST: TYPE_DEL ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_14
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|140032500388736| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
AC-4 missing client cert_dir fail PASS
AC-5 server forced reject plain business PASS
[2026-08-22 22:49:36]|Error|rpc/rpc-io.cpp:133 rpc_handshake_client_negotiate|140032500388736| handshake: server downgraded to plain but mTLS requested, abort
AC-6 no-downgrade PASS
AC-7 plain-only startup PASS
mixed_mtls_link_integration: PASS
PASS

=== TEST: VARIOUS OFFSETS - 偏移组合 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_15
PASS

=== TEST: VARIOUS SIZES - 不同文件大小 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_16
PASS

=== TEST: OVERWRITE - 同一偏移重复写入 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_17
PASS

=== TEST: MIXED OPERATIONS - 混合操作序列 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_18
PASS

=== TEST: SPARSE FILE - 稀疏文件 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_19
PASS

=== TEST: OUT_OF_ORDER WRITE - 乱序写入 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_20
[2026-08-22 22:49:36]|Error|rdbcomm/rdbcommd-main.c:271 main|140153277498240| args process failed
PASS

=== TEST: ZERO OFFSET + VARIOUS COUNT - 零偏移+不同大小 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_21
[2026-08-22 22:49:36]|Error|rdbcomm/rdbcommd-main.c:271 main|140235699827584| args process failed
PASS

=== TEST: LARGE GAP - 大间隔写入 ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_22
[2026-08-22 22:49:36]|Error|rpc/rpc-client.cpp:1219 args_process|139629888914304| aio-speed: invalid --mtls-enable: 2
[2026-08-22 22:49:36]|Error|rpc/rpc-client.cpp:672 client_main|139629888914304| Error: init aio-speed arguments failed
PASS

=== TEST: TYPE_NEW - Multi Write ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_23
[2026-08-22 22:49:36]|Error|rpc/rpc-client.cpp:1228 args_process|140349359207296| aio-speed: invalid --tls-algorithm: TLS_UNKNOWN
[2026-08-22 22:49:36]|Error|rpc/rpc-client.cpp:672 client_main|140349359207296| Error: init aio-speed arguments failed
PASS

=== TEST: TYPE_NEW - Reopen ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_24
PASS

=== TEST: TYPE_NEW - Delete ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_25
PASS

=== TEST: TYPE_UPDATE - Delete ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_26
PASS

=== TEST: DELETE then CREATE ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_27
PASS

=== TEST: DELETE then MODIFY ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_28
PASS

=== TEST: OPEN EXIST ===
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_30
PASS

=== TEST: RANDOM WRITE ===
  After OnOpen: type=1 size=5000 size_ext=5000 byte_id=0
  GetVal returns 0, type=1
  OnWriteFile ret=0
  After OnWriteFile: type=1 size=5000 size_ext=5000 byte_id=0
[2026-08-22 22:49:36]|Info|fs-backup/public/fs_meta.cpp:118 DeleteFsMeta|267973632| delete /tmp/fs_meta_test_31
PASS

========================================
       Results: 0 failures
========================================
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784177579712| Applied ciphersuites config: TLS_SM4_GCM_SM3
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784180487040| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
[2026-08-22 22:49:36]|Info|libs/tls_cert.c:90 tls_cert_set_ciphersuites|139784177579712| Applied ciphersuites config: TLS_AES_256_GCM_SHA384
PASSED

=== Results ===
Passed: 8
Failed: 0

All tests PASSED!

report of tests:
[0m[38;2;0;255;0;1m[  2%]:[0m access/default ........................ [38;2;0;255;0;1mpassed[0m [1m0.025s[0m
[0m[38;2;0;255;0;1m[  5%]:[0m chmod/default ......................... [38;2;0;255;0;1mpassed[0m [1m0.025s[0m
[0m[38;2;0;255;0;1m[  7%]:[0m chown/default ......................... [38;2;0;255;0;1mpassed[0m [1m0.025s[0m
[0m[38;2;0;255;0;1m[ 10%]:[0m dir_tree/default ...................... [38;2;0;255;0;1mpassed[0m [1m0.025s[0m
[0m[38;2;0;255;0;1m[ 12%]:[0m download_fileat/default ............... [38;2;0;255;0;1mpassed[0m [1m0.023s[0m
[0m[38;2;0;255;0;1m[ 15%]:[0m download_file_dir/default ............. [38;2;0;255;0;1mpassed[0m [1m0.020s[0m
[0m[38;2;0;255;0;1m[ 17%]:[0m download_fileats/default .............. [38;2;0;255;0;1mpassed[0m [1m0.025s[0m
[0m[38;2;0;255;0;1m[ 20%]:[0m download_link/default ................. [38;2;0;255;0;1mpassed[0m [1m0.022s[0m
[0m[38;2;0;255;0;1m[ 22%]:[0m fchmodats/default ..................... [38;2;0;255;0;1mpassed[0m [1m0.021s[0m
[0m[38;2;0;255;0;1m[ 25%]:[0m fchownats/default ..................... [38;2;0;255;0;1mpassed[0m [1m0.020s[0m
[0m[38;2;0;255;0;1m[ 27%]:[0m download_file/default ................. [38;2;0;255;0;1mpassed[0m [1m0.029s[0m
[0m[38;2;0;255;0;1m[ 30%]:[0m dir_utils_dir_copy_test/default ....... [38;2;0;255;0;1mpassed[0m [1m0.036s[0m
[0m[38;2;0;255;0;1m[ 32%]:[0m execute_command/default ............... [38;2;0;255;0;1mpassed[0m [1m0.029s[0m
[0m[38;2;0;255;0;1m[ 35%]:[0m LRUCache_test/default ................. [38;2;0;255;0;1mpassed[0m [1m0.017s[0m
[0m[38;2;0;255;0;1m[ 37%]:[0m logger_test/default ................... [38;2;0;255;0;1mpassed[0m [1m0.021s[0m
[0m[38;2;0;255;0;1m[ 40%]:[0m lstat/default ......................... [38;2;0;255;0;1mpassed[0m [1m0.019s[0m
[0m[38;2;0;255;0;1m[ 42%]:[0m metadata/default ...................... [38;2;0;255;0;1mpassed[0m [1m0.020s[0m
[0m[38;2;0;255;0;1m[ 45%]:[0m mixed_mtls_test/default ............... [38;2;0;255;0;1mpassed[0m [1m0.019s[0m
[0m[38;2;0;255;0;1m[ 47%]:[0m mkdirall/default ...................... [38;2;0;255;0;1mpassed[0m [1m0.019s[0m
[0m[38;2;0;255;0;1m[ 50%]:[0m mkdir/default ......................... [38;2;0;255;0;1mpassed[0m [1m0.018s[0m
[0m[38;2;0;255;0;1m[ 52%]:[0m pread/default ......................... [38;2;0;255;0;1mpassed[0m [1m0.018s[0m
[0m[38;2;0;255;0;1m[ 55%]:[0m dmsbtex_session_test/default .......... [38;2;0;255;0;1mpassed[0m [1m0.051s[0m
[0m[38;2;0;255;0;1m[ 57%]:[0m pwrite/default ........................ [38;2;0;255;0;1mpassed[0m [1m0.020s[0m
[0m[38;2;0;255;0;1m[ 60%]:[0m rdb_config_test/default ............... [38;2;0;255;0;1mpassed[0m [1m0.016s[0m
[0m[38;2;0;255;0;1m[ 62%]:[0m mkdir_path_test/default ............... [38;2;0;255;0;1mpassed[0m [1m0.023s[0m
[0m[38;2;0;255;0;1m[ 65%]:[0m lmdb_dict_test/default ................ [38;2;0;255;0;1mpassed[0m [1m0.037s[0m
[0m[38;2;0;255;0;1m[ 67%]:[0m lmdb_sort_test/default ................ [38;2;0;255;0;1mpassed[0m [1m0.035s[0m
[0m[38;2;0;255;0;1m[ 70%]:[0m libobk_session_test/default ........... [38;2;0;255;0;1mpassed[0m [1m0.039s[0m
[0m[38;2;0;255;0;1m[ 72%]:[0m readlink/default ...................... [38;2;0;255;0;1mpassed[0m [1m0.012s[0m
[0m[38;2;0;255;0;1m[ 75%]:[0m readdir/default ....................... [38;2;0;255;0;1mpassed[0m [1m0.015s[0m
[0m[38;2;0;255;0;1m[ 77%]:[0m rpc_net_time_test/default ............. [38;2;0;255;0;1mpassed[0m [1m0.010s[0m
[0m[38;2;0;255;0;1m[ 80%]:[0m rpc_own_handshake_test/default ........ [38;2;0;255;0;1mpassed[0m [1m0.010s[0m
[0m[38;2;0;255;0;1m[ 82%]:[0m symlink/default ....................... [38;2;0;255;0;1mpassed[0m [1m0.006s[0m
[0m[38;2;0;255;0;1m[ 85%]:[0m readdir_tree/default .................. [38;2;0;255;0;1mpassed[0m [1m0.014s[0m
[0m[38;2;0;255;0;1m[ 87%]:[0m upload_fileats/default ................ [38;2;0;255;0;1mpassed[0m [1m0.005s[0m
[0m[38;2;0;255;0;1m[ 90%]:[0m rdbcomm_handshake_session_test/default  [38;2;0;255;0;1mpassed[0m [1m0.031s[0m
[0m[38;2;0;255;0;1m[ 92%]:[0m mixed_mtls_integration/default ........ [38;2;0;255;0;1mpassed[0m [1m0.055s[0m
[0m[38;2;0;255;0;1m[ 95%]:[0m rpc_tool_integration/default .......... [38;2;0;255;0;1mpassed[0m [1m0.073s[0m
[0m[38;2;0;255;0;1m[ 97%]:[0m fs_meta_comprehensive_test/default .... [38;2;0;255;0;1mpassed[0m [1m0.126s[0m
[0m[38;2;0;255;0;1m[100%]:[0m tls_cert_test/default ................. [38;2;0;255;0;1mpassed[0m [1m0.245s[0m
[0m
[38;2;0;255;0;1m100%[0m tests passed, [38;2;255;0;0;1m0[0m test(s) failed out of [1m40[0m, spent [1m0.301s[0m 全量重建为准——增量构建对"删结构体字段+测试未同步改"组合会静默放过旧二进制（T0360/T0361 连续两次中招）

## Verdict

- verdict_id: V-T0361-20260822-01
- outcome: confirmed
- reason: 四条 AC 全过（evidence-test/evidence-test-v2）；两次提交 4f0e880+2456402 含完整版本递增与披露；用户发现的遗漏已在 Check 内闭环
- at: 2026-08-22T22:50:28+08:00
