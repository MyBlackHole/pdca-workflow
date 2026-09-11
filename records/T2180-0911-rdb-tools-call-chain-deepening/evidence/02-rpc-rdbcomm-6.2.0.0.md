# rpc 与 rdbcomm Knowledge Map（知识地图）

> **文档定位**：本文是传输通道子系统的导航—— **「通道能力 → 代码位置 → 握手契约」**：需要远端执行、文件传输、鉴权握手时读什么、改哪里、核对什么常量。
>
> **前置阅读**：《00-index》（路由矩阵）
> **阅读约定**：路径一律相对 `6200/release`；`file:line` 行号易变动，以符号名为准
> **依据**：aio-tools 6200/release 实际代码 + 仓内引用统计（基线：目录 6200/release，commit fe9d4364）
> **版本化**：本文为 6.2.0.0 版代码地图，地图与代码基线强绑定；读前先按 00-index §〇 版本路由选版本，再读对应目录下的 `<tag>.md`
> **最后更新**：2026-09-10

---

## 1. 模块组织总览

| 目录/文件 | 职责 | 关键文件 |
|---|---|---|
| `rpc/main.cpp` | `aio-speedd` 服务端入口：配置/daemon/鉴权/unix-sock/TLS | `rpc/main.cpp:302`（`client_main`→`StartRpcService`） |
| `rpc/rpc-server.cpp/.h` | 服务端监听/分发：accept → TLS/鉴权 → 按 `uiMT` 分发 | `rpc/rpc-server.cpp:69`（`RPCServiceThread`），`:178`（分发） |
| `rpc/rpc-client.cpp` + `aio-speed.cpp` | `aio-speed` 客户端 CLI：参数解析 + method 分发 | `rpc/rpc-client.cpp:698,749` |
| `rpc/rpc.cpp/.h` | 核心会话 + 持久连接 + 块传输 | `rpc_session_start/restart/stop`，`rpc_conn_start/restart`，`do_new_conn`，`rpc_download/upload_block` |
| `rpc/rpc-conn.cpp/.h` | 持久连接封装 + LZ4/异或 | `new_rpc_conn/rpc_conn_send_msg/recv_msg/reconn_send/is_ready_recv` |
| `rpc/rpc-msg.c/.h` | 最简帧 `u32 len + body` | `rpc_send_msg/rpc_recv_msg` |
| `rpc/rpc-io.cpp/.h` | 带超时/限速帧 | `rpc_send/rpc_recv/connect_server/connect_server2` |
| `rpc/rpc-protocol.h/.cpp` | 消息契约：`MT_*` + 大小端转换 | `rpc/rpc-protocol.h:11` |
| `rpc/rpc-config.cpp/.h` | 配置：ini 解析/默认值/双缓冲热加载 | `rpc/rpc-config.cpp:130` |
| `rpc/backup-client.cpp` / `restore-client.cpp` / `meta-client.cpp` | 备份/恢复/meta 高层编排（被 rpc-client 调用） | `rpc/rpc-client.cpp:17` |
| `rpc/rpc-command.cpp` / `rpc-public.cpp` | 旧单连接 scp/download 实现（`do_scp_download` 等） | `rpc/rpc-command.cpp:34` |
| `rpc/rpc-common.cpp` / `file-stat.cpp` / `utils.c` / `crc32.c` | 目录遍历/加解密/file_stat 编解码/crc | `rpc/rpc-common.cpp:446` |
| `rdbcomm/client.c/.h` | rdb 客户端：连接/文件上下传/模块管理/远端命令 | `rdbcomm/client.c:33`（`rdbcomm_new`） |
| `rdbcomm/server.c` + `rdbcommd-main.c` + `msg.c` + `module.c` | rdb 服务端：INIT 鉴权 + OPEN/READ/WRITE/CLOSE + 模块管理 | `rdbcomm/server.c:593` |
| `rpc-keygen/main.c` | timed_key 生成器（仅 dba/ops，人工运维用） | `rpc-keygen/main.c:8,36` |

> **一句话记忆**：rpc 是「短会话办小事、持久连接办批量」，rdbcomm 是「另一套文件+模块通道」，timed_key 是「两者的共同门票」，bwlimit 是「油门（限速）」。

---

## 2. 能力总览（能力 → 代码 → 使用方）

| 能力 | 解决什么问题 | 核心代码位置 | 主要入口 | 使用方 |
|---|---|---|---|---|
| **短会话连接** | 一次建链办一件事 | `rpc/rpc.cpp`（`rpc_session_start` → `connect_server`） | `rpc_session_start` | `rpc-client.cpp:713,754,767`；fs-backup（`fsclient/cli.cpp:720,903`，`fsdeamon/backup_helper.cpp:144`，`transfer_file.cpp:601,761`） |
| **持久连接 + 断线重连** | 复用 fd 做批量操作 | `rpc/rpc.cpp`（`rpc_conn_start/do_new_conn/rpc_conn_restart`）+ `rpc-conn.cpp`（`rpc_conn_reconn_send_msg`） | `rpc_conn_start` | `backup-client.cpp:732,1009`；`restore-client.cpp:551,792`；`transfer_file.cpp:585` |
| **握手/鉴权** | timed_key 防未授权 | `rpc/rpc.cpp`（`rpc_key_verify`）+ `rpc-server.cpp:326` + `libs/timed_key.c:169` | `rpc_key_verify/timed_key_verify` | `rpc-client.cpp:721`；`rdbcomm/server.c:594` |
| **消息收发** | 帧同步/超时/限速 | `rpc/rpc-io.cpp`（`rpc_send/recv`）+ `rpc-msg.c`（`rpc_send_msg/recv_msg`） | `rpc_conn_send_msg/recv_msg` | `rpc.cpp` 20+ 处；`rpc-server.cpp:3815,3923` |
| **文件块传输** | 断点/压缩/校验传输 | `rpc/rpc.cpp`（`rpc_download/upload_block_*`）+ `rpc-command.cpp`（`do_scp_download`） | `do_scp_download/rpc_download_block` | `transfer_file.cpp:316`；`cli.cpp:727`；`backup_helper.cpp:839` |
| **目录/属性** | 远端 ls/stat/chmod | `rpc/rpc.cpp`（`rpc_conn_cli_readdir/lstat/pread` 等）+ `rpc-server.cpp`（`rpc_conn_srv_*`） | `rpc_conn_cli_*` | `rpc/tests/*` 全系；`rpc-client.cpp:2701,3057` |
| **远端命令下发** | 远端 shell | `rpc/rpc-server.cpp`（`execute_cmd`）+ `rdbcomm/client.c`（`execute_cmd`） | `execute_cmd` | `tests/execute_command.cpp:51`；`rdbcomm-main.c:202` |
| **rdb 文件上下传** | rdb 模块文件通道 | `rdbcomm/client.c`（`file_download/file_upload/send_open/read/write/close`） | `rdbcomm_connect + file_download` | `rdbcomm-main.c:130,137,160,167` |
| **rdb 模块管理** | 插件注册启停 | `rdbcomm/client.c`（`module_register/unregister/start/stop/list`） | `module_register` | `rdbcomm-main.c:249`；`server.c:927` |
| **key 生成** | 运维发 key | `rpc-keygen/main.c`（`timed_key_create`）+ `libs/timed_key.c:142` | `rpc-keygen -u dba` | 仓内无代码调用，仅人工/脚本 |

---

## 3. 核心任务链

### 3.1 rpc 短会话

```
client_main（rpc-client.cpp:705）
  → rpc_session_start（rpc.cpp:141）
  → connect_server（rpc-io.cpp:202，socket + keepalive + 可选 bind + connect）
  → sec_tls_enabled 分支：tls_cert_client_handshake + detach（rpc-io.cpp:260）
  → rpc_key_verify（rpc.cpp:90，data_encrypt + msg_key_verify_hton + rpc_send/recv）
  → 业务（execute_shell_script / rpc_download_file / rsync_*，rpc-client.cpp:740,760）
  → rpc_session_stop（rpc.cpp:177）
```

### 3.2 rpc 持久连接

```
rpc_conn_start（rpc.cpp:2378）
  → connect_server + new_rpc_conn（rpc-conn.cpp:13）
  → do_new_conn（rpc.cpp:2313，MT_EXECUTE_NEW_CONN + flags + rpc_send/recv + read_is_ready）
  → rpc_conn_reconn_send_msg → rpc_send_msg（rpc-conn.cpp:162）
  → rpc_conn_is_ready_recv_msg → read_is_ready + rpc_recv_msg（rpc-conn.cpp:245）
```

### 3.3 服务端分发

```
main → RpcService::StartRpcService（main.cpp:387，rpc-server.cpp:56）
  → RPCServiceThread（bind/listen/accept，rpc-server.cpp:69）
  → RPCService → create_thread(StartRPCServiceWoker)（rpc-server.cpp:156）
  → tls_cert_server_handshake + detach（rpc-server.cpp:199）
  → read_is_ready + rpc_recv + msg_base_ntoh（rpc-server.cpp:215）
  → if (uiMT == MT_*) 分发（rpc-server.cpp:238,326,386）
```

### 3.4 rdbcomm 通道

```
rdbcomm_new（client.c:33）
  → rdbcomm_connect（client.c:98，socket + keepalive/snd/rcvtimeo + connect
      + sec_tls_enabled 握手 client.c:151 + RDBCOMM_INIT + flags + timeo + key）
  → send_open → get_handle（client.c:352）
  → send_read / send_write（client.c:392,430）
  → file_download / upload 循环 DATA/EOF + get_status + send_close（client.c:506,626）
服务端：process_init（data_dencrypt + timed_key_verify，server.c:583）
```

### 3.5 key 生成

```
is_allowed_user（dba/ops，rpc-keygen/main.c:8）
  → timed_key_create(user, expire_hours)（libs/timed_key.c:136）
  → _timed_key_create（pack + Feistel + base64，timed_key.c:142）
```

---

## 4. 协议契约（逐字摘录，拼错即失败）

### 4.1 端口与常量

| 契约 | 值 | 出处 |
|---|---|---|
| rpc 默认端口 | `6611`（`DEFAULT_RPC_PORT`） | `rpc/rpc-config.h:35` |
| 锁文件 | `/tmp/rpc_daemon.pid` | `rpc/rpc-config.h:43` |
| unix sock | `aio-speed.sock` | `rpc/main.cpp:254` |
| rdb 最大消息 | `5MB`（`RDBCOMM_MAX_MSG_LENGTH`） | `rdbcomm/rdbcomm.h:9` |
| rdb 默认端口 | 无法确认（`rdbcomm-main.c` 仅 `atoi(optarg)`，未见默认值） | 标记待补 |

### 4.2 MT_ 消息号（节选）

`rpc/rpc-protocol.h:12,65,68,71`：`MT_EXECUTE_SHELL_SCRIPT 0x00001000`，`MT_EXECUTE_SCP_DOWNLOAD 0x00001102`，`MT_EXECUTE_NEW_CONN 0x00001117`，`MT_KEY_VERIFY 0x00001119`，`MT_GET_TIME 0x0000111A`。全表以 `rpc-protocol.h` 为准。

rdb：`RDBCOMM_INIT 1 / OPEN 2 / CLOSE 4 / READ 5 / WRITE 6 / … / EXEC_CMD 11` + `MSG_STATUS 101 / HANDLE 102 / DATA 103 / NODATA 104`（`rdbcomm/rdbcomm.h:11,26`）。

### 4.3 帧与握手字段

- 帧 = `htonl(len) + body`（`rpc-io.cpp:128`，`libs/rpc-net.c:61`）。
- 消息头 `msg_base__ { unsigned int uiMT; unsigned int uiLEN; }`（`rpc-protocol.h:52`）；`NORMAL_RESP 0x80000000`（`:11`）；`MSG_BUFF_LEN 0x80000`，`MSG_RESP_BUFF_LEN 0x4000000`（`:49`）。
- rpc 握手 `msg_new_conn__ { flags/sndtimeo/rcvtimeo/keepalive/conn_id/b/c/d }`（`rpc-protocol.h:104`）。
- rdb 握手 `buf_put_u8(INIT) + u32(mid) + u32(flags) + u32(sndtimeo) + u32(rcvtimeo) + cstring(key)`（`client.c:195`）。

### 4.4 timed_key 机制

- `KEY_LEN 12`，`USER_LEN 4`（`libs/timed_key.h:23`）；合法用户 `rdb/dba/ops`（`timed_key.c:20`），但 rpc-keygen 仅放行 `dba/ops`（`rpc-keygen/main.c:10`）。
- 混淆 `secret[4] = {111,127,233,211}` 异或（`rpc-common.cpp:446`）；过期按分钟比较（`timed_key.c:150,196`）。
- 总开关 `key_is_enabled → sec_auth_enabled`（`timed_key.c:225`）；rpc-keygen 编译时 `-DRPC_KEYGEN` 绕过（`rpc-keygen/xmake.lua:5`）。

### 4.5 超时重试

`read_timeout 120000`，`retry 3`，`keepalive 30`，`parallel 4`（`rpc-config.cpp:137`，`rpc-config.h:34,39`）；`RPC_CONN_RETRY` / `RPC_SESSION_OPT_RETRY` 宏（`rpc-conn.h:29`，`rpc.h:343`，sleep(1) 重试）。

---

## 5. 新能力如何复用或扩展

```
→ 新远端命令 → 服务端 rpc-server.cpp 加 MT_ 分支 + rpc-protocol.h 加消息号 + 客户端加 rpc_conn_cli_* 封装
→ 新传输模式 → 参照 do_scp_download / rpc_download_block（rpc-command.cpp / rpc.cpp）
→ 新 rdb 模块 → client.c module_register 范式 + server.c 模块管理（server.c:927）
→ 新鉴权方式 → 先过 libs timed_key 总开关（见 03），勿在 rpc 内另起炉灶
→ 超时/并发调整 → rpc-config 默认值 + 调用方 flags，勿硬编码
```

**不应放入 rpc**：业务语义（备份/恢复逻辑归 fs-backup）、通用基础能力（归 libs）、新存储介质（归 04）。

---

## 6. 影响范围

| 组件 | 使用方 | 修改后必须检查 |
|---|---|---|
| `rpc-protocol.h`（MT_ 常量） | client + server 全链路 + fs-backup 转发 | 两侧同步；拼错即走 default |
| `rpc-io.cpp`（帧/超时/限速） | 全部会话与连接 | 全通道回归；bwlimit 联动 |
| `timed_key` 机制 | rpc + rdbcomm 鉴权 | 两通道鉴权回归 |
| `rpc-config` 默认值 | 全部连接行为 | 超时/重试语义变化全量回归 |

---

## 7. 孤岛与分叉

- `rpc_get_time / MT_GET_TIME`：服务端有实现（`rpc-server.cpp:386`），但仓内无业务调用方——对时孤岛。
- `connect_server2`：仅被旧 ioctl 路径调用（`rpc.cpp:1320,1542`），新链路走 `connect_server`——过渡残留。
- `rpc_conn_reconn`：头文件注释、实现仍被内部调用——经头文件不可见，外部勿直接调。
- `MT_GET_TIME` 在 `rpc/rpc-protocol.h` 与 `libs/rpc-net-protocol.h` 保持同值：前者由 aio-speedd 解码，后者由 `libs/rpc-net.c:rpc_get_time` 生产，形成 C++ 服务端与 C 客户端 codec 两端。
- `rpc/crc32.c` 与 `libs/crc32.c` 分属不同 target 的同类实现；调用链应按链接 target 分辨，不能仅凭同名文件互换。
- `main.go` 与 rpc 零引用：它只是内核模块安装器（见 05），不是 rpc 的一部分。

---

## 8. 分支差异

- 本分册基于 6.2.0.0（`6200/release`，`fe9d4364`，如 `rpc_version=3.6.4.19`）。他分支版本号与协议字段若有差异，差异补记于此，当前为空（待实证）。

- `rdbcomm/rdbcommd` 默认端口为 `6610`（`rdbcommd-main.c:39,211`）；`aio-speedd/aio-speed` 的 RPC 默认端口为 `6611`（`rpc/rpc-config.h:35`）。两者不能按“rpc 通道”合并引用。

## 9. aio-speed ↔ aio-speedd 逐操作调用链

状态：`aio-speed=current client`，`aio-speedd=current service`。两条线协议并存：短会话用 `rpc/rpc-protocol.h:MT_*`；`MT_EXECUTE_NEW_CONN` 升级后的持久连接用 `rpc/rpc.h:NEW_CONN_TMP_*`。不得把后者写成 `MT_*`。

### 9.1 aio-speed 公开操作清单

入口公共前缀：`rpc/aio-speed.cpp:main -> rpc/rpc-client.cpp:client_main -> args_process`。互斥业务操作如下；其余 `--remote/--local/--parallel/--compress/...` 是参数，不是独立操作。

| CLI 操作 | client_main 分发 | 核心实现 |
|---|---|---|
| `--backup-full` / `--backup-inc` | `rpc_args.method=rpc_backup` + `full=true/false` | `rpc/backup-client.cpp:rpc_backup` |
| `--backup-merge` | `method=rpc_backup_merge` | `rpc/backup-client.cpp:rpc_backup_merge` |
| `--restore-file` | `method=rpc_restore_file` | `rpc/restore-client.cpp:rpc_restore_file` |
| `--restore-meta` | `method=rpc_restore_meta` | `rpc/restore-client.cpp:rpc_restore_meta` |
| `--meta-find` / `--meta-find-range` | `rpc_meta_find/rpc_meta_find_range` | `rpc/meta-client.cpp` |
| `--proc-progress` | `rpc_proc_progress` | `rpc/proc-progress.cpp:rpc_proc_progress` |
| `-c` / `--get-uuid` | `g_handler=1` | `execute_shell_script`（后者固定 `cat UNION_ID_FILE_PATH`） |
| `--download` / `--upload` | `g_handler=1000/1008` | `rpc_download_file/rpc_upload_file` |
| `--tree` | `g_handler=1006` | `list_dir_tree_02` |
| `--nc` | `g_handler=1010` | `nc_extend_operation` |
| `--fb-item` | `g_handler=1013` | `rsync_download_file` |
| `--fb-list-item` | `g_handler=1017` | `rsync_list_file`（本地 `session=NULL`） |
| `--fb-item-size` | `g_handler=1020` | `rsync_download_file_size` |
| `--fb-item-upload` | `g_handler=1022` | `rsync_upload_file` |
| `--reload-config` / `--show-config` | `g_handler=1026/1029` | unix socket 管理通道 |

### 9.2 服务启动、TLS/鉴权与通用返回

```text
rpc/main.cpp:main
  -> rpc/rpc-config.cpp:rpc_init_config -> args_process
  -> tls_cert_init_server_from_env -> bandwidth_init(RPC_SERVER_ID)
  -> rpc/rpc-server.cpp:StartRpcService
  -> RpcService::StartServiceThread / SocketService::OnAccept（TCP 6611）
  -> RpcService::RPCService -> create_thread(StartRPCServiceWoker)
  -> RpcService::StartRPCServiceWoker
     -> [sec_tls_enabled] tls_cert_server_handshake -> tls_cert_detach_ssl
     -> rpc_recv -> msg_base_ntoh -> if/else(uiMT)
```

客户端需要鉴权时：`client_main -> rpc_session_start -> rpc_key_verify` 构造 `MT_KEY_VERIFY`，服务端 `StartRPCServiceWoker` 解密 key 后调 `libs/timed_key.c:timed_key_verify`，用 `MT_KEY_VERIFY_RESP` 返回 `err`；失败即关闭连接。业务响应统一以 `NORMAL_RESP | request MT` 或连接子协议响应回到客户端并写 `rpc_args.error_no`。

### 9.3 代表性业务链

**新备份/恢复链（持久连接，超过五个符号节点）：**

```text
rpc/rpc-client.cpp:client_main（--backup-full/--backup-inc）
  -> rpc/backup-client.cpp:rpc_backup
  -> rpc/rpc.cpp:rpc_conn_start -> do_new_conn
  -> rpc/rpc.cpp:rpc_conn_cli_readdir_tree / rpc_conn_cli_lstat
  -> rpc/rpc-conn.cpp:rpc_conn_reconn_send_msg
  -> rpc/rpc-server.cpp:RpcService::StartRPCServiceWoker（MT_EXECUTE_NEW_CONN）
  -> rpc/rpc-server.cpp:new_conn
  -> switch NEW_CONN_TMP_READDIR_TREE/LSTAT
  -> rpc_conn_srv_readdir_tree/rpc_conn_srv_lstat
  -> dir_traversal_at/lstat
返回：rpc_conn_send_msg -> rpc_conn_recv_msg -> backup-client 的目录任务队列/LMDB meta -> 本地备份树
```

```text
rpc/rpc-client.cpp:client_main（--restore-file）
  -> rpc/restore-client.cpp:rpc_restore_file
  -> rpc/rpc.cpp:rpc_conn_start -> do_new_conn
  -> rpc_conn_cli_mkdirall / rpc_conn_cli_upload_fileats / rpc_conn_cli_symlink
  -> rpc/rpc-server.cpp:new_conn
  -> rpc_conn_srv_mkdirall / rpc_conn_srv_upload_fileats / rpc_conn_srv_symlink
  -> mkdir_path/write/symlink
返回：逐项 status -> restore thread/checkpoint/progress -> error_no
```

**旧 download/upload 短会话：**

```text
rpc/rpc-client.cpp:client_main（g_handler=1000）
  -> rpc_session_start -> rpc_download_file
  -> rpc/rpc.cpp:rpc_download_block_start/rpc_download_block
  -> rpc/rpc-io.cpp:rpc_send（MT_EXECUTE_DOWNLOAD_BLOCK）
  -> rpc/rpc-server.cpp:StartRPCServiceWoker
  -> OnMsgDownloadBlock -> pread/read
返回：MT_EXECUTE_DOWNLOAD_BLOCK_RESP + 数据/校验 -> rpc_download_block_finish -> 本地文件
```

upload 同构：`rpc_upload_file -> rpc_upload_block_start/rpc_upload_block -> MT_EXECUTE_UPLOAD_BLOCK -> OnMsgUploadBlock -> pwrite/write -> *_RESP`。`-c` 使用 `execute_shell_script -> MT_EXECUTE_SHELL_SCRIPT -> execute_cmd -> SHELL_COMMAND_CONTINUE/COMPLETED`；`--nc` 使用 `nc_extend_operation -> MT_EXECUTE_NC_EXTEND -> nc_extend` 后让连接进入字节转发，二者处理后服务端离开主循环。

### 9.4 MT_* 生产端 ↔ 消费端全表

| 请求常量 | 客户端生产符号 | aio-speedd 消费符号 |
|---|---|---|
| `MT_EXECUTE_SHELL_SCRIPT` | `execute_shell_script` | `execute_cmd` |
| `MT_EXECUTE_SCP_DOWNLOAD` | `do_scp_download/rpc_download_file` | `rpc_scp_download` |
| `MT_EXECUTE_SCP_DOWNLOAD_LINK` | `do_scp_download_link` | `rpc_scp_download_link` |
| `MT_EXECUTE_DIR_TREE` | `list_dir_tree_02` | `rpc_dir_tree` |
| `MT_EXECUTE_BATCH_LIST_DIR_TREE` | `do_batch_list_dir_tree` | `rpc_list_batch_dir_tree` |
| `MT_EXECUTE_IS_DIR` | `do_is_dir` | `OnMsgIsDir` |
| `MT_EXECUTE_SCP_UPLOAD` | `rpc_upload_file` | `OnMsgScpUpload` |
| `MT_EXECUTE_DOWNLOAD_BLOCK` | `rpc_download_block` | `OnMsgDownloadBlock` |
| `MT_EXECUTE_UPLOAD_BLOCK` | `rpc_upload_block_start/rsync_upload_block/rpc_upload_block_finish` | `OnMsgUploadBlock` |
| `MT_EXECUTE_FILE_STAT` | `rpc_file_stat[_batch]` | `OnMsgFileStat` |
| `MT_EXECUTE_FILE_EXISTED` | `rpc_file_existed` | `OnMsgFileExisted` |
| `MT_EXECUTE_IOCTL_FSBACKUP` | `do_fsbacup_dev_ioctl` | `OnIOCTLFsbackupDev` |
| `MT_EXECUTE_NC_EXTEND` | `nc_extend_operation` | `nc_extend` |
| `MT_EXECUTE_MKDIR` | `do_remote_mkdir` | `remote_mkdir` |
| `MT_EXECUTE_UNLINK` | `do_remote_unlink` | `remote_unlink` |
| `MT_EXECUTE_NEW_DIR_TREE` | `do_dir_tree_new` | `on_dir_tree` |
| `MT_EXECUTE_NEW_CONN` | `do_new_conn` | `new_conn` |
| `MT_KEY_VERIFY` | `rpc_key_verify` | `timed_key_verify` 分支 |
| `MT_GET_TIME` | `libs/rpc-net.c:rpc_get_time`（由 `timed_net_key.c` 调用） | inline get-time 分支 |

### 9.5 persistent opcode 全表

`rpc/rpc.h:NEW_CONN_TMP_*` 的 1–19 在发送端 `rpc/rpc.cpp:rpc_conn_cli_*` 与接收端 `rpc/rpc-server.cpp:new_conn` 逐项闭合：`NEW_CONN_TMP_LSTAT -> rpc_conn_srv_lstat`、`NEW_CONN_TMP_READDIR -> rpc_conn_srv_readdir`、`NEW_CONN_TMP_PREAD -> rpc_conn_srv_pread`、`NEW_CONN_TMP_PWRITE -> rpc_conn_srv_pwrite`、`NEW_CONN_TMP_MKDIR -> rpc_conn_srv_mkdir`、`NEW_CONN_TMP_FCHOWNATS -> rpc_conn_srv_fchownats`、`NEW_CONN_TMP_FCHMODATS -> rpc_conn_srv_fchmodats`、`NEW_CONN_TMP_DOWNLOAD_FILEATS -> rpc_conn_srv_download_fileats`、`NEW_CONN_TMP_UPLOAD_FILEATS -> rpc_conn_srv_upload_fileats`、`NEW_CONN_TMP_READLINK -> rpc_conn_srv_readlink`、`NEW_CONN_TMP_SYMLINK -> rpc_conn_srv_symlink`、`NEW_CONN_TMP_ACCESS -> rpc_conn_srv_access`、`NEW_CONN_TMP_MKDIRALL -> rpc_conn_srv_mkdirall`、`NEW_CONN_TMP_CHMOD -> rpc_conn_srv_chmod`、`NEW_CONN_TMP_CHOWN -> rpc_conn_srv_chown`、`NEW_CONN_TMP_OPENAT -> rpc_conn_srv_openat`、`NEW_CONN_TMP_DOWNLOAD_FILEAT -> rpc_conn_srv_download_fileat`、`NEW_CONN_TMP_READLINKAT -> rpc_conn_srv_readlinkat`、`NEW_CONN_TMP_READDIR_TREE -> rpc_conn_srv_readdir_tree`。`NEW_CONN_TMP_NO=0` 是哨兵，不是公开操作。返回统一经 `rpc_conn_send_msg/rpc_conn_recv_msg`，断线发送由 `rpc_conn_reconn_send_msg -> rpc_conn_restart` 重建 `MT_EXECUTE_NEW_CONN`。

## 10. rpc-keygen 调用链

状态：`operator + build-only`，`rpc-keygen/xmake.lua` 设置 `set_default(false)`。

```text
rpc-keygen/main.c:main
  -> 参数分支 -u(dba|ops) / -e(hours) / -v / -h
  -> rpc-keygen/main.c:is_allowed_user（拒绝 rdb 与其它用户）
  -> libs/timed_key.c:timed_key_create
  -> encrypt_data -> Base64 编码
返回：stdout "Key: ..."；该 key 在 rpc_key_verify/timed_key_verify 和 rdbcomm process_init/timed_key_verify 消费
```

## 11. rdbcomm ↔ rdbcommd 逐操作调用链

状态：两者均为 `external runtime`：target 与完整双端实现存在，但 aio-tools 仓内无主业务调用者。

### 11.1 入口、连接与 INIT

```text
rdbcomm/rdbcomm-main.c:main
  -> args_process（-c/--df/--uf/--mr/--ms/--mq/--mu/--ml）
  -> opts.handler
  -> rdbcomm/client.c:rdbcomm_new -> rdbcomm_connect
  -> client.c:rdbcomm_connect（内联构造 RDBCOMM_INIT + flags/timeouts/key）
  -> rdbcomm/msg.c:send_msg（u32 length + buf，可选 data_encrypt）
  -> TCP 6610
  -> rdbcomm/server.c:server_start -> server_loop -> accept -> connection_create
  -> server.c:on_connect -> get_msg -> handlers[RDBCOMM_INIT]
  -> server.c:process_init -> timed_key_verify -> send_status
返回：RDBCOMM_MSG_STATUS/OK；失败时 CLI handler 释放 connection 并返回 EXIT_FAILURE
```

服务启动链：`rdbcomm/rdbcommd-main.c:main -> args_process -> [daemon] supervise -> tls_cert_init_server_from_env -> server_create -> server_start`；每连接可先 `tls_cert_server_handshake -> detach_ssl`，之后进入上述自定义帧。

### 11.2 文件 download/upload

```text
--df
rdbcomm-main.c:do_download_file -> rdbcomm_connect
  -> rdbcomm/client.c:file_download
  -> client.c:send_open（RDBCOMM_OPEN/O_RDONLY）
  -> server.c:process_open -> open/fstat -> handle_new -> send_handle
  -> client.c:send_read（RDBCOMM_READ + handle）
  -> server.c:process_read -> handle_to_fd -> read 循环 -> RDBCOMM_MSG_DATA
  -> client write(local_path)
  -> client.c:send_close（RDBCOMM_CLOSE） -> server.c:process_close -> handle_close
返回：最终 RDBCOMM_MSG_STATUS -> do_download_file -> main
```

```text
--uf
rdbcomm-main.c:do_upload_file -> rdbcomm_connect
  -> rdbcomm/client.c:file_upload
  -> client.c:send_open（RDBCOMM_OPEN/O_WRONLY|O_CREAT|O_TRUNC）
  -> server.c:process_open -> handle_new -> RDBCOMM_MSG_HANDLE
  -> client.c:send_write（RDBCOMM_WRITE + handle，随后 DATA 分块）
  -> server.c:process_write -> handle_to_fd -> recv DATA -> write
  -> client.c:send_close -> process_close
返回：STATUS -> 本地 errno/退出码
```

### 11.3 command 与模块操作

| CLI 操作 | 客户端链 | 服务端分发/结果 |
|---|---|---|
| `-c` | `do_execute_cmd -> execute_cmd(RDBCOMM_EXEC_CMD)` | `process_cmd -> ppopen/read -> DATA/NODATA -> ppclose -> STATUS` |
| `--mr` | `do_module_register -> module_register(RDBCOMM_MODULE_REGISTER)` | `process_module_register -> module_manager_register -> STATUS` |
| `--mu` | `do_module_unregister -> module_unregister` | `process_module_unregister -> module_manager_unregister -> STATUS` |
| `--ms` | `do_module_start -> module_start` | `process_module_start -> module_manager_start -> STATUS` |
| `--mq` | `do_module_stop -> module_stop` | `process_module_stop -> module_manager_stop -> STATUS` |
| `--ml` | `do_module_list -> module_list` | `process_module_list -> module_manager_list -> DATA -> STATUS` |

### 11.4 opcode 与返回契约

`rdbcomm/rdbcomm.h` 发送/消费端已闭合：`RDBCOMM_INIT=1`、`RDBCOMM_OPEN=2`、`RDBCOMM_CLOSE=4`、`RDBCOMM_READ=5`、`RDBCOMM_WRITE=6`、`RDBCOMM_MODULE_REGISTER=7`、`RDBCOMM_MODULE_UNREGISTER=8`、`RDBCOMM_MODULE_START=9`、`RDBCOMM_MODULE_STOP=10`、`RDBCOMM_EXEC_CMD=11`、`RDBCOMM_MODULE_LIST=12`；返回类型为 `RDBCOMM_MSG_STATUS=101`、`RDBCOMM_MSG_HANDLE=102`、`RDBCOMM_MSG_DATA=103`、`RDBCOMM_MSG_NODATA=104`。`rdbcomm/client.c` 和 `rdbcomm/server.c:handlers` 是两端权威。真实仓外调用、模块 `.so` 内容和目标主机权限需部署联调。
