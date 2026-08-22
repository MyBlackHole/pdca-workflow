# T0354 详细执行计划（implement.md）

## 前置事实（已核查）

| 项目 | 客户端入口 | 服务端入口 | 明文现状 |
|------|-----------|-----------|---------|
| rdbcomm | `io.c: rdb_hs_client_session_init` ← `client.c:166` | `server.c:439 on_connect → rdb_hs_server_first_stage` | 总是发协商 / 总是等握手 |
| dmsbtex | `network.c: sbt_session_client_init` ← `sbt.c:258` | `network.c: sbt_session_server_accept` ← `main.c:214` | 同上 |
| libobk | `libobk.c:121 sbt_session_client_init` ← `:352` | `oracleCmdTbl.c:67 sbt_session_server_accept` ← `:797` | 同上 |

rpc 基线：`rpc-io.cpp:82 rpc_ensure_handshake` —— `!mtls_enabled → hs_done=true, return 0`。

## 切片 A：rdbcomm（预计 3 文件）

### A1. `rdbcomm/io.c — rdb_hs_client_session_init`
```c
if (!session || fd < 0)
    return -EINVAL;
/* 对齐 rpc 按需握手：明文模式零握手帧 */
if (!mtls_enabled) {
    rdb_hs_session_init_plain(session, fd);
    return 0;
}
```
（原无条件 `init_plain + negotiate` 移入 mtls_enabled=1 分支之后）

### A2. `rdbcomm/server.c — on_connect`
在 ca_cn 计算之前插入：
```c
if (!conn->server->options.mtls_enabled) {
    /* 明文部署：connection_create 已 init_plain，跳过首阶段等待 */
    goto serve_;
}
...原 ca_cn/first_stage 逻辑...
serve_:
while (1) { ...业务循环... }
```
（`conn->io` 已由 `connection_create:531` init_plain，无需补初始化）
注意 label 与变量作用域调整（hs_result/ca_cn 移入分支内或提前声明）。

### A3. `rdbcomm/tests/handshake_session_test.c`
- 「明文协商 + 回声」用例 → 重命名「明文零握手直通」：server 线程不再调 `first_stage`，改为 `init_plain` 后直接 read/write 回声；client 侧不调 `client_session_init`，`init_plain` 后直发。
- mTLS 正向、强制拒绝两用例保持原断言不变。
- 验证：`xmake build rdbcomm rdbcommd rdbcomm_handshake_session_test && xmake run ...`

## 切片 B：dmsbtex（1 文件 + 测试注释）

### B1. `dmsbtex/network.c — sbt_session_client_init` 入口
```c
if (!cfg->mtls_enabled) {
    dm_hs_session_init_plain(io, fd);
    return 0;
}
```

### B2. `dmsbtex/network.c — sbt_session_server_accept` 入口
```c
if (!cfg->mtls_enabled) {
    dm_hs_session_init_plain(io, fd);
    return 0;
}
```
（ca_cn 解析/negotiate/TLS 升级全部保留在 mtls_enabled=1 分支内）

### B3. `dmsbtex/test/session_test.c`
- AC-3 注释更新为「明文零握手直通」（断言逻辑天然覆盖，无需改结构）。
- AC-1 mTLS / AC-4a/b 保持不变（prepare 前置校验仍生效）。
- 验证：build + run 全绿。

## 切片 C：libobk（2 文件）

### C1. `libobk/lib/sbt/libobk.c — sbt_session_client_init` 入口
```c
if (!ctx->tls_mtls_enabled) {
    obk_hs_session_init_plain(io, fd);
    return 0;
}
```

### C2. `libobk/lib/logic/oracleCmdTbl.c — sbt_session_server_accept` 入口
```c
if (!cfg->mtls_enabled) {
    obk_hs_session_init_plain(io, fd);
    return 0;
}
```

### C3. 验证：`xmake build sbt FileTransferAgent libobk_session_test libobk_protocol_test` + 双测试运行全绿。

## 切片 D：全量验证 + 收尾

1. `xmake build -r` 零错误。
2. `xmake test` 全绿（40+）。
3. grep 断言（AC-5）：三项目明文短路分支存在性
   - `grep -A2 "if (!mtls_enabled)" rdbcomm/io.c` 等 6 处。
4. 登记证据 → commit → advance check。

## 风险与回退

- 唯一行为变化 = 明文模式不再有握手往返；新旧混布明文将帧错位断连（PRD 已声明，三端同步升级）。
- mTLS 路径零触碰：任一回归可即时定位到入口短路（单点 revert 即恢复）。
