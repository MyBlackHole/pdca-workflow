# dmsbtex 服务端 ca_cn 缺帧修复（AC-2）

文件：`dmsbtex/network.c`，`dm_server_handshake` 的 `ca_cn unavailable` 分支。

## 修复前

```c
if (!cn || !cn[0]) {
    ErrorLog("handshake: ca_cn unavailable");
    return -1;
}
```

直接断开，未发送 `HANDSHAKE_RESP` 拒绝帧。

## 修复后（与同文件 no-TLS-context / unknown-algorithm 分支及 rpc/rdbcomm 对齐）

```c
if (!cn || !cn[0]) {
    ErrorLog("handshake: ca_cn unavailable");
    result_net = htons(DM_HS_ERR_CA_CN);
    alg_net = 0;
    memcpy(body, &result_net, 2);
    memcpy(body + 2, &alg_net, 2);
    memset(&host, 0, sizeof(host));
    host.cmd = CMD_HANDSHAKE_RESP;
    host.bytes = 4;
    send_packet(io, (char *)&host, (char *)&net, body, 4);
    return -1;
}
```

## 说明

- `DM_HS_ERR_CA_CN` 枚举已定义（`dmsbtex/protocol.h:104` = `0x8006`），此前该分支漏用。
- 对齐 `rpc`（`HS_ERR_CA_CN`，`rpc-server.cpp:284-297`）与 `rdbcomm`（`RDB_HS_ERR_CA_CN`，`server.c:517-521`）。
- 测试同步新增 `DM_HS_ERR_CA_CN` 可达性断言（`dmsbtex/test/session_test.c`）。
