# libs Knowledge Map（知识地图）

> **文档定位**：本文是公共 C 库的导航—— **「公共能力 → 代码位置 → 使用方」**：面对一个需求时，判断「已有公共能力在哪里、能否直接复用、不够时该扩展哪个文件、什么时候不该放进 libs」。
>
> **前置阅读**：《00-index》（路由矩阵）
> **阅读约定**：路径一律相对 `6200/release`；「使用方」指本仓库内的实际引用位置（均经 grep 实证）；`file:line` 行号易变动，以符号名为准
> **依据**：aio-tools 6200/release 实际代码 + 仓内引用统计（基线：目录 6200/release，commit fe9d4364）
> **版本化**：本文为 6.2.0.0 版代码地图，地图与代码基线强绑定；读前先按 00-index §〇 版本路由选版本，再读对应目录下的 `<tag>.md`
> **最后更新**：2026-09-10

---

## 1. 模块组织总览

`libs/` 是全仓的**纯公共库**（无业务决策、无备份语义、无通道编排），按能力域组织：

| 文件组 | 能力域 | 说明 |
|---|---|---|
| `ae.c/.h` + `anet.c/.h` | 网络 | ae 事件循环（epoll 封装，源自 redis）；anet socket 工具 |
| `buf*.c` + `buf.h` + `buf-err.*` | 序列化 | OpenBSD buf：`buf_new/put_u32/get_string_direct` 等 |
| `crypt.c/.h` + `tls_cert.c/.h` + `tls_keygen.c/.h` | 加密/TLS | `data_encrypt` 异或；`tls_cert_*` OpenSSL 双向认证；`tls_keygen_*` CA/签发 |
| `thread.c/.h` + `thread_pool.c/.h` | 线程 | 裸 `create_thread` + 固定线程池队列 |
| `lmdb_dict.*` / `lmdb_multi_dict.*` / `lmdb_queue.*` / `lmdb_stack.*` + `lmdb/` | KV 存储 | LMDB 上封装字典/多库/队列/栈 |
| `rpc-net.c` + `rpc-net-protocol.c/.h` | rpc-net | 极简取时协议客户端 |
| `timed_key.c/.h` + `timed_net_key.c/.h` | 鉴权 | Feistel+Base64 时效 key；联网取时版 |
| `logger.c/.h` + `rdb-config.c/.h` | 基础 | `InfoLog/ErrorLog`；inih + `sec_*_enabled` 总开关 |
| `unix_ipc.c/.h` + `common.c/.h` + `misc.c/.h` + `dir_utils.c/.h` | 基础 | unix 域管理通道；`sock_*/mkdir_path`；大小端；目录遍历/拷贝 |
| `bitmap.c/.h` + `bitmap2.h` + `lz4.c/.h` + `crc32.c/.h` + `LRUCache.h` | 数据结构 | 位图/压缩/校验/模板 LRU |
| `compat.h` + `recallocarray.c` + `timingsafe_bcmp.c` + `libs.h` | 兼容 | OpenBSD 移植；`libs.h` 仅含 `timed_key.h` |
| `tests/*` + `timed_net_key_python/*` | 测试/绑定 | 各模块单测；`timed_net_key` 的 Cython wheel |
| `xmake.lua` + `version.in` | 构建 | 定义 `tools/logger/rdb-config/rpc-net/tls_cert/timed_key/timed_net_key/tls-keygen` |

> **一句话记忆**：buf 是「封包语言」，thread_pool 是「并发苦力」，lmdb_* 是「落地记忆」，timed_key + tls_cert 是「门禁」，rdb-config 是「总电闸」，logger 是「嘴」。

---

## 2. 能力总览（能力 → 代码 → 使用方）

| 能力 | 解决什么问题 | 核心代码位置 | 主要入口 | 使用方 |
|---|---|---|---|---|
| **序列化** | buf 跨 rpc/rdbcomm 封包 | `libs/buf.h:25,149,187` | `buf_new` 开辟 + `put_u32/get_string_direct` | `rdbcomm/client.c:49`，`rdbcomm/server.c:533`，`rpc/rpc-conn.cpp:25`，`libs/unix_ipc.c:143` |
| **本地鉴权** | key 生成/校验/过期 | `libs/timed_key.c:136,169,225` + Feistel `encrypt_data:68` | `timed_key_create/verify/key_is_enabled` | 生成 `rpc-keygen/main.c:66`；校验 `rpc/rpc-server.cpp:344`，`rdbcomm/server.c:593`；门控 `rpc-client.cpp:705`，`rdbcomm-main.c:539` |
| **TLS 双向认证** | 通道加密 + 身份认证 | `libs/tls_cert.h:31,40` + `tls_cert.c:414,633` | 客户端 `tls_cert_init_client_from_env`，服务端 `tls_cert_server_handshake` | `rpc-client.cpp:645`，`rpc-server.cpp:200`，`rdbcomm/server.c:433`，`fsdeamon/main.cpp:348`，`fsclient/main.cpp:561` |
| **KV 字典** | 元数据持久化 | `libs/lmdb_dict.h:35` + `lmdb_multi_dict.h:46` | `lmdb_*_open` + `begin/commit_txn` | 字典 `fs-backup/public/meta.cpp:41` + `rpc/rpc-metadata.c:192`；多库仅 fs-backup（`fs_meta.cpp:61`） |
| **KV 队列/栈** | 枚举/传输任务持久队列 | `libs/lmdb_queue.h:35` + `lmdb_stack.h:27` | `lmdb_queue_create/enqueue/dequeue` | `restore-client.cpp:629,636,665`，`backup-client.cpp:843,851,859` |
| **线程池** | 并发下载/上传分片 | `libs/thread_pool.h:50` + `thread_pool.c:144,207,341` | 先 `init` 再循环 `post`，`wait` 收尾 | `transfer_file.cpp:213,620`，`backup-client.cpp:343,1030`，`restore-client.cpp:299,812`，`s3file/main.cpp:497,551` |
| **裸线程** | 常驻服务线程 | `libs/thread.h:10` | `create_thread`（函数指针） | `rpc-server.cpp:59`，`rdbcomm/server.c:350`，`unix_server.cpp:72` |
| **管理通道** | reload/show 配置 | `libs/unix_ipc.h:27,29` + `unix_ipc.c:441,464`（内部 `ae_main`） | 服务端注册回调，客户端 `execute_unix_show_config` | `fsdeamon/unix_server.cpp:63`，`rpc/main.cpp:390`，`rpc-client.cpp:678` |
| **配置总开关** | tls/auth/audit 统一门控 | `libs/rdb-config.h:58,65` + `rdb-config.c:222,230` | `sec_tls_enabled/sec_auth_enabled`（env > `[security]` > `[auth]enable`） | `rpc-net.c:154`，`timed_key.c:227`，`rpc-io.cpp:260` |
| **对称加扰** | 协议体混淆 | `libs/crypt.h:8` | `data_encrypt/dencrypt` | `rpc-conn.cpp:146`（全包加密），`rpc.cpp:113`，`rpc-server.cpp:339`，`rdbcomm/msg.c:35`，`server.c:588` |
| **目录工具** | 递归遍历/拷贝 | `libs/dir_utils.h:25,30` + `common.h:33` | `dir_traversal_at/dir_copy_at`（回调式）+ `mkdir_path` | `rpc-server.cpp:43`，`fs_meta.cpp:577`，`backup_helper.cpp:17` |

---

## 3. 关键机制

### 3.1 timed_key 鉴权

`pack(uid<<40 | expire分钟)` → 4 轮 Feistel（`ROUND_KEYS` + `0x9e3779b9`）→ 11 字符 Base64（`timed_key.c:47,68,109`）；`round_offset = now % 4`，解密轮询 4 种 offset 试出合法 uid（0-2 对应 rdb/dba/ops，`timed_key.c:81,20`）；`verify` 比较 `expire > now/60`（`:193`）；总开关 `key_is_enabled → sec_auth_enabled`（`:225`）。

### 3.2 TLS 证书

路径常量 `/opt/aio/cfg/certs/ca.crt/host.crt`（`common.h:14-26`）；客户端 `tls_cert_init_client_from_env → init_client`，服务端每连接 `tls_cert_server_handshake` 后 `detach_ssl` 转明文 fd 继续走自有协议（rpc-net/rdbcomm 同模式）；`verify_is_local` 已注释化（`tls_cert.c:212,461,528`）。

### 3.3 rpc-net 取时协议

`u32 len(htonl) + body` 成帧（`rpc-net.c:57,11`）；body 仅 `msg_get_time{uiMT,uiLEN}` / `resp{uiResult,timestamp}`（`rpc-net-protocol.h:16,21`）；`rpc_server_connect` 做 `socket + keepalive + connect + [sec_tls_enabled ? client_handshake + detach_ssl : 明文]`（`rpc-net.c:130-178`）。

### 3.4 线程池

`queue + running 双队列 + cond + waiting 计数`（`thread_pool.h:36`）；`thread_task_post(handler, ctx)` 入队，工作线程循环取任务，`thread_pool_wait` 插哨兵 `wait_handler`（`thread_pool.c:144,207,341`）；典型链「按分片数 init N 个池 → 循环 post → wait/destroy」。

### 3.5 版本注入（构建侧，详见 05）

根 `xmake.lua:12-23` 硬编码版本 → `set_configvar` → `version.h.in` / `version.log.in` 渲染。`libs/version.in` 仅 `${TLS_KEYGEN_VERSION}` 一行。

---

## 4. 继承与分层：调用方向

```
业务层（fs-backup / rpc / rdbcomm / s3tools）
  → libs 能力层（buf / thread_pool / lmdb_* / timed_key / tls_cert / dir_utils / logger / rdb-config）
  → 系统层（ae-epoll / OpenSSL / LMDB /iminining）
```

- **组合而非继承**：C 语言无继承，各模块按需调用 libs 函数，无统一基类（与 05 文档中 Python `Base → Sys` 链不同，勿套用）。
- **注意独立拷贝**：`xbsa/src/utils/thread_pool.*` 是独立拷贝，非本库（见 04）——改本库线程池不影响 xbsa。

---

## 5. 新能力如何复用或扩展

```
新需求需要某个能力
 → ① 搜 §2 总表：这个能力是不是已经存在？
 → ② 存在 → 直接调用；看 §6 影响范围确认改动面
 → ③ 不存在但相近 → 扩展已有文件（如新 KV 结构参照 lmdb_dict 范式；新加扰算法参照 crypt.c）
 → ④ 全新能力域 → 新增 .c/.h（放 libs/ 根）+ libs/xmake.lua 加 target
```

**什么情况下不应该放入 libs**（全仓最硬的一条边界）：

- **业务决策与备份语义**：备份策略、source 管理、快照语义属于 fs-backup（见 01）。
- **通道编排**：会话管理、MT_ 分发、握手流程属于 rpc/rdbcomm（见 02）。
- **一次性逻辑**：只被一个调用方用到、无复用价值的逻辑，留在调用方模块内——libs 的每一行都会被所有二进制链接。
- **介质专属逻辑**：S3/XBSA/SBT 专属实现归 04 各模块，勿塞进 libs。

---

## 6. 影响范围

| 组件 | 使用方 | 修改后必须检查 |
|---|---|---|
| `buf.h`（序列化） | rpc + rdbcomm 封包 | 两通道封包/解包回归 |
| `timed_key.c`（鉴权） | rpc + rdbcomm + rpc-keygen | 两通道鉴权回归；过期语义变化全量回归 |
| `tls_cert.*` | 全部 TLS 通道 | 证书路径/握手语义变化全量回归 |
| `thread_pool.*` | fsclient + backup/restore + s3file | 并发语义变化多模块回归（xbsa 独立拷贝不受影响） |
| `lmdb_*` | fs-backup meta + rpc 队列 | 事务语义变化两模块回归 |
| `rdb-config`（总开关） | 全部安全门控 | 开关语义变化全仓回归 |
| `logger` / `tools` | 全仓 | 几乎所有 target 的 `add_deps` 第一项 |

---

## 7. 孤岛与未确认

- `timed_net_key.c`：C 仓零业务调用，仅 Python pyx 调用——孤岛，C 新代码勿引用。
- `timed_net_key_python/`：仅 `xmake.lua:57-73` 打包 wheel，无 C/C++ 引用。
- `tls_cert_verify_is_local`：仅声明 + 测试注释，生产零调用。
- `tests/bitmap_tools.c`、`rand_io_main.c`：有 target 无 `add_tests`，全仓零引用。
- `anet.c tcp_*`：业务零调用；`anet_unix_*` 未全量 grep——标记无法确认。
- `bitmap2.h`：内联位操作，全仓 `bitmap_*(` 命中皆为 `bitmap.h` 系——疑似备用头。
- `lz4/crc32` 真实业务调用量：被头文件自声明淹没，需二次精确过滤——标记无法确认。

---

## 8. 分支差异

- 本分册基于 6.2.0.0（`6200/release`，`fe9d4364`）。他分支的 libs 若有差异，差异补记于此，当前为空（待实证）。

## 9. bwlimit_tools 逐子命令调用链

状态：CLI 为 `operator`；`bwlimit/lib` 为 `current`，由 `rpc/rpc-io.cpp` 上传/下载数据面调用。入口 `bwlimit/main.c:main -> demos[]`。

```text
set_bandwidth <upload> <download>
bwlimit/main.c:main
  -> bwlimit/main_set_bandwidth.c:demo_set_bandwidth_main
  -> atoll + bytes/s 到 bits/s 转换
  -> bwlimit/lib/bandwidth.c:bandwidth_init(TEST2)
  -> bwlimit/lib/config.c:configs_alloc/configs_get
  -> bwlimit/lib/shm_comm.c:shm_create/shm_get -> shm_attach（共享 configs_t）
  -> bwlimit/lib/bandwidth.c:bandwidth_config_update
  -> bwlimit/lib/config.c:configs_update
  -> bandwidth_exit -> configs_put -> shm_detach
返回：stdout 当前总上传/下载 MB/s
```

| 子命令 | 分发与核心链 | 结果/消费关系 |
|---|---|---|
| `meta` | `demo_meta_main -> bandwidth_init(TEST3) -> configs_get_configs -> 遍历 configs_t.confs -> bandwidth_exit` | 打印 SHM id、总带宽、每 app 活跃数/带宽 |
| `reset <client_id>` | `demo_reset_main -> 范围检查 -> bandwidth_init(client_id) -> config_reset -> bandwidth_exit` | 清该共享配置；退出码 |
| `set_bandwidth` | 见上方完整链 | 更新总上下行配额 |
| `version` / `-v` / `--version` | `demo_version_main -> BWLIMIT_VERSION` | stdout 版本 |

运行时数据面闭环：`rpc/main.cpp:main -> bandwidth_init(RPC_SERVER_ID)` 与 `rpc/rpc-client.cpp:client_main -> bandwidth_init(RPC_CLIENT_ID)` 注册；收发时 `rpc/rpc-io.cpp:rpc_send/rpc_recv -> bandwidth_limit(BW_OP_UPLOAD/BW_OP_DOWNLOAD)` 读取同一 SHM 配置并节流。CLI 不在每次传输链中启动。

## 10. tls-keygen 逐子命令调用链

状态：`operator`。公共入口：`libs/tls_keygen.c:main` 先处理全局 `--version/--help`，再把 `create/ca/sign` 映射到 handler。

**create：生成主机私钥和 CSR**

```text
libs/tls_keygen.c:main（subcmd=create）
  -> handle_create -> getopt_long（output/force/cn/key/csr）
  -> [output 或 cn] libs/common.c:mkdir_path
  -> tls_keygen_create
  -> EVP_PKEY_CTX_new_id(EVP_PKEY_ED25519) -> EVP_PKEY_keygen
  -> PEM_write_PrivateKey -> chmod(0600)
  -> read_cn_from_file(HOST_ID_FILE)
  -> X509_REQ_new -> X509_NAME_add_entry_by_txt(CN)
  -> X509_REQ_set_pubkey -> X509_REQ_sign -> PEM_write_X509_REQ
返回：host.key + host.csr 路径；错误映射 TLS_KEYGEN_ERR_*
```

**ca：生成自签 CA**

```text
main（subcmd=ca） -> handle_ca（强制 -n/--cn）
  -> [output] mkdir_path
  -> tls_keygen_create_ca
  -> EVP_PKEY_keygen(Ed25519) -> PEM_write_PrivateKey/chmod(0600)
  -> X509_new -> set serial/notBefore/notAfter/version/subject/issuer/pubkey
  -> X509V3_EXT_nconf_nid(basicConstraints=critical,CA:TRUE)
  -> X509_sign -> PEM_write_X509
返回：ca.key + ca.crt
```

**sign：用 CA 签主机证书**

```text
main（subcmd=sign） -> handle_sign -> getopt_long（ca-cert/ca-key/key/csr/out/days）
  -> [output 或 cn] mkdir_path
  -> tls_keygen_sign
  -> PEM_read_X509(ca cert) + PEM_read_PrivateKey(ca key)
  -> PEM_read_X509_REQ + X509_REQ_verify
  -> X509_new -> copy CSR subject/pubkey -> set issuer/validity
  -> X509_sign(ca key) -> PEM_write_X509(out)
返回：host.crt；失败返回 TLS_KEYGEN_ERR_*
```

产物消费链：`libs/tls_cert.c:tls_cert_init_client_from_env/tls_cert_init_server_from_env` 读取 CA/host cert/key，进入 `rpc`、`rdbcomm`、`fs-cli/fsdeamon` 的 TLS 握手。静态源码只证明路径和调用，证书部署权限与双方信任链需环境验证。
