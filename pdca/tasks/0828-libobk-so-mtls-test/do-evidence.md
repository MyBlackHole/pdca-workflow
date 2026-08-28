# Do 阶段证据（Evidence）— T3991-0828-libobk-so-mtls-test

## 实现产物

- 新增 `libobk/test/rman_mtls_test.c`：模仿 RMAN 经 SBT API 调用 libobk.so 验证 mTLS 的端到端测试程序。
- 修改 `libobk/xmake.lua`：新增 `libobk_rman_mtls_test` 目标（`set_kind("binary")`、`add_files("test/rman_mtls_test.c")`、`add_deps("sbt","logger","tls_cert")`、`add_defines("TEST_CERT_DIR=...libs/tests/certs")`、`add_tests("default", {realtime_output = true})`）。

## 构建验证

```
$ xmake build libobk_rman_mtls_test
[100%]: build ok, spent 0.5s
```

## 运行验证（连续两次，稳定）

运行命令：`build/linux/x86_64/release/libobk_rman_mtls_test`

两次运行输出尾部一致，均包含：

```
[PASS] AC-1 mTLS backup closed-loop via SBT API succeeded
[PASS] AC-2 fail-closed: server mTLS off -> client sbtinit2 rejected
[PASS] AC-3 fail-closed: algorithm mismatch -> client sbtinit2 rejected
[PASS] rman_mtls_test: all AC passed
```

关键运行时日志佐证：

- AC-1 握手成功：`recvOpenBackupSliceResponse ok, peer[/tmp/] has done`；`sbtclose2`/`sbtend` 收响应 `retCode: 0`。
- AC-2 fail-closed：`handshake: short read on negotiate response: fd=4 expect=234`（服务端不 mTLS，客户端等不到明文握手响应帧而失败）。
- AC-3 fail-closed：`handshake: algorithm 0x0002 rejected by server lock (locked=0x0001)`（服务端锁 SM4=0x0001，客户端用 AES=0x0002，被拒）。

## 调试修复记录（Do 阶段踩坑，供复盘）

| # | 现象 | 根因 | 修复 |
|---|------|------|------|
| 1 | `connect to [:0] failure` | `sbtinit2` 内部读静态 `env` 结构体（由 `setSbtEnv()` 从 getenv 填充），但 `sbtinit2` 不自动调 `setSbtEnv()`；`setenv(AIO_SERV_HOST/PORT)` 未刷进结构体 | 测试侧显式 `extern void setSbtEnv();` 并调用（参考 `libobk/test/test.c:263`） |
| 2 | 服务端 TLS 用 `/opt/aio/cfg/certs` 而非 `TEST_CERT_DIR` | 服务端 `sbt_server_tls_config_init` 经 `PARAM_CERT_DIR`/`RPC_TLS_CERT_DIR` 读证书目录，但该 env 在 `fork` 之后的 `client_backup` 才设，子进程继承不到 | 在 `main` 的 `fork` 前注入 `RPC_TLS_CA_CERT`/`RPC_TLS_CLIENT_CERT`/`RPC_TLS_CLIENT_KEY`/`RPC_TLS_CERT_DIR`/`AIO_SBT_LOGPATH`（参考 `session_test.c:84-87`） |
| 3 | 编译报 `expected 'int' but argument is of type 'void *'` | `sbt_server_tls_config_init` 第二参是 `int cli_mtls`（非 `const char* ca_cn`），误传 `NULL` | 传 `mtls_enabled`（int） |
| 4 | `_baseRecv ... after [-1]` 业务响应失败 | 客户端 `g_compress_enabled=1`，对服务端明文响应帧 `uncompress` 并校验 `org_bytes` | `client_backup` 在 `setSbtEnv()` **之前** `setenv("AIO_ENABLE_COMPRESS","0")`；响应帧补 `rh.org_bytes = sizeof(int)` |
| 5 | `bind: Address already in use` | 早期失败运行残留 `fork` 出的 server 子进程占用端口 | 修复使正常路径 `waitpid` 清理子进程；用例端口范围改为 28081-28083 避开残留 |

## 结论

libobk 作为 SBT 库被 RMAN 类客户端（经 `sbtinit2→sbtbackup→sbtclose2→sbtend`）调用时，mTLS 握手与备份控制帧闭环正常；且服务端 mTLS 关闭 / 算法错配时客户端 `sbtinit2` 坚定失败（fail-closed，不降级明文）。AC-1/2/3 全部达成，测试已纳入 xmake test CI 目标。

## xmake test 框架验证（AC-4，正确调用格式）

测试标识符格式为 `目标名/组名`（非裸 target 名，亦非 `组/目标名`）；根用户需 `--root -y`（同仓库 `oss/test/xmake_go_test.sh` 范式）。裸名 / `组/目标名` / `目标名/*` 均会 `nothing to test`（xmake 框架行为，非测试失效）。

```
$ xmake test --root -y "libobk_rman_mtls_test/default"
[PASS] AC-1 mTLS backup closed-loop via SBT API succeeded
[PASS] AC-2 fail-closed: server mTLS off -> client sbtinit2 rejected
[PASS] AC-3 fail-closed: algorithm mismatch -> client sbtinit2 rejected
[PASS] rman_mtls_test: all AC passed
report of tests:
[100%]: libobk_rman_mtls_test/default  passed  0.729s
100% tests passed, 0 test(s) failed out of 1, spent 0.725s
```

连续两次运行均 `100% tests passed`，稳定通过。

---
*由 Do 阶段登记。Check 阶段据此写 conclusion.md 并获取 verdict。*
