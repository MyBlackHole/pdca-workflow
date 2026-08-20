# T0333 详细修改计划（Do 阶段）

方向：rdb-config 只做基础查询，CLI 覆盖状态与全部 TLS 参数归各调用方持有，通过各结构体显式字段传给库模块。

## 一、`libs/rdb-config.{c,h}` — 基础配置层

### 1. 移除 cli 覆盖状态与接口

- `rdb-config.h`：删除 `sec_tool_tls_set_cli_overrides` 声明（106-107 行）。
- `rdb-config.c`：
  - 删除 static 全局 `cli_mtls_set/cli_mtls_enabled/cli_algorithm`（216-218 行）。
  - 删除 `sec_tool_tls_set_cli_overrides` 函数（325-338 行）。
  - `sec_cache_reset`（220-228 行）删除 `cli_mtls_set = 0; cli_algorithm = NULL;` 两行，保留 master 缓存重置。

### 2. `sec_tool_tls_enabled/algorithm` 保持纯查询

- `sec_tool_tls_enabled`（283-302）：移除 cli 分支后为 env→config→master 纯查询。
- `sec_tool_tls_algorithm`（304-323）：移除 cli 分支后为 env→config→ciphersuites→default。
- `sec_tls_cert_path`/`sec_tls_client_cert_paths`/`sec_tls_ca_cn`（340-381）保留，作为基础路径解析工具供工具 main 使用。

### 3. 测试断言更新（`libs/tests/rdb_config_test.c`）

- 删除 319-327 行 `sec_tool_tls_set_cli_overrides` 相关断言（`(1,1,AES)`、`(1,2,NULL)`、`(0,0,"TLS_UNKNOWN")`）。
- 保留纯查询断言（300-318 行 env/config 优先级）。
- 新增：验证无 cli 状态时 `sec_tool_tls_enabled/algorithm` 返回 env/config 正确值。

## 二、四个工具 main — 注入层（自持覆盖并填充结构体）

### 通用模式

```c
int mtls_enabled = sec_tool_tls_enabled(SECTION, ENV_MTLS);
if (opts.cli_mtls_set)
    mtls_enabled = opts.cli_mtls_enabled;
const char *alg = sec_tool_tls_algorithm(SECTION, ENV_ALG);
if (opts.cli_algorithm)
    alg = opts.cli_algorithm;
/* 填入结构体 + 解析 TLS env 到结构体字段 */
```

### 1. `rdbcomm/rdbcomm-main.c`

- **删除** 599-601（time 分支）与 609-610（常规）两处 `set_cli_overrides` 调用。
- **合并并填充** `opts.copts`（client_options，需先扩展字段见三.1）：
  ```c
  int mtls = sec_tool_tls_enabled(RDBCOMM_TOOL_SECTION, RDBCOMM_MTLS_ENABLE_ENV);
  if (opts.cli_mtls_set)
      mtls = opts.cli_mtls_enabled;
  const char *alg = sec_tool_tls_algorithm(RDBCOMM_TOOL_SECTION,
                                           RDBCOMM_TLS_ALGORITHM_ENV);
  if (opts.cli_algorithm)
      alg = opts.cli_algorithm;
  opts.copts.mtls_enabled = mtls;
  opts.copts.tls_algorithm = rpc_hs_algorithm_from_name(alg);
  opts.copts.ca_cn = sec_tls_ca_cn();
  opts.copts.ca_cert = sec_tls_cert_path("RPC_TLS_CA_CERT", CA_CERT_PATH);
  opts.copts.cert_dir = sec_tls_cert_path("RPC_TLS_CERT_DIR", DEFAULT_CERT_DIR);
  snprintf(opts.copts.client_cert, sizeof(opts.copts.client_cert), "%s",
           sec_tls_cert_path("RPC_TLS_CLIENT_CERT", ""));
  snprintf(opts.copts.client_key, sizeof(opts.copts.client_key), "%s",
           sec_tls_cert_path("RPC_TLS_CLIENT_KEY", ""));
  ```
- 合并逻辑放 time 分支判断之后（约 612 行）。

### 2. `rdbcomm/rdbcommd-main.c`

- **删除** 311-313 行 `set_cli_overrides` 调用。
- **合并并填充** `server_opts`（server_options，需扩展见三.2）：
  ```c
  int tool_mtls_enabled = sec_tool_tls_enabled(RDBCOMMD_TOOL_SECTION,
                                               RDBCOMMD_MTLS_ENABLE_ENV);
  if (opts.cli_mtls_set)
      tool_mtls_enabled = opts.cli_mtls_enabled;
  const char *tool_alg = sec_tool_tls_algorithm(RDBCOMMD_TOOL_SECTION,
                                                RDBCOMMD_TLS_ALGORITHM_ENV);
  if (opts.cli_algorithm)
      tool_alg = opts.cli_algorithm;
  server_opts.mtls_enabled = tool_mtls_enabled;
  server_opts.tls_algorithm = rpc_hs_algorithm_from_name(tool_alg);
  server_opts.ca_cn = sec_tls_ca_cn();
  server_opts.ca_cert = sec_tls_cert_path("RPC_TLS_CA_CERT", CA_CERT_PATH);
  server_opts.server_cert = sec_tls_cert_path("RPC_TLS_SERVER_CERT", HOST_CERT_PATH);
  server_opts.server_key = sec_tls_cert_path("RPC_TLS_SERVER_KEY", HOST_KEY_PATH);
  ```

### 3. `rpc/rpc-client.cpp`

- **删除** 671-677 行 `set_cli_overrides` 调用。
- **合并并填充** `g_rpc_config`（需扩展见三.3）：
  ```c
  int mtls = sec_tool_tls_enabled(AIO_SPEED_TOOL_SECTION, AIO_SPEED_MTLS_ENABLE_ENV);
  if (g_rpc_args->cli_mtls_set)
      mtls = g_rpc_args->cli_mtls_enabled;
  const char *alg = sec_tool_tls_algorithm(AIO_SPEED_TOOL_SECTION,
                                           AIO_SPEED_TLS_ALGORITHM_ENV);
  if (!g_rpc_args->cli_algorithm.empty())
      alg = g_rpc_args->cli_algorithm.c_str();
  g_rpc_config->mtls_enabled = mtls;
  g_rpc_config->tls_algorithm = rpc_hs_algorithm_from_name(alg);
  snprintf(g_rpc_config->ca_cn, sizeof(g_rpc_config->ca_cn), "%s", sec_tls_ca_cn());
  snprintf(g_rpc_config->ca_cert, sizeof(g_rpc_config->ca_cert), "%s",
           sec_tls_cert_path("RPC_TLS_CA_CERT", CA_CERT_PATH));
  snprintf(g_rpc_config->cert_dir, sizeof(g_rpc_config->cert_dir), "%s",
           sec_tls_cert_path("RPC_TLS_CERT_DIR", DEFAULT_CERT_DIR));
  snprintf(g_rpc_config->client_cert, sizeof(g_rpc_config->client_cert), "%s",
           sec_tls_cert_path("RPC_TLS_CLIENT_CERT", ""));
  snprintf(g_rpc_config->client_key, sizeof(g_rpc_config->client_key), "%s",
           sec_tls_cert_path("RPC_TLS_CLIENT_KEY", ""));
  ```

### 4. `rpc/main.cpp`

- **删除** 400-407 行 `set_cli_overrides` 调用。
- **合并并填充** `g_rpc_config`（服务端，需扩展见三.3）：
  ```c
  int mtls = sec_tool_tls_enabled(AIO_SPEEDD_TOOL_SECTION, AIO_SPEEDD_MTLS_ENABLE_ENV);
  if (g_rpc_config->cli_mtls_set)
      mtls = g_rpc_config->cli_mtls_enabled;
  const char *alg = sec_tool_tls_algorithm(AIO_SPEEDD_TOOL_SECTION,
                                           AIO_SPEEDD_TLS_ALGORITHM_ENV);
  if (g_rpc_config->cli_algorithm[0])
      alg = g_rpc_config->cli_algorithm;
  g_rpc_config->mtls_enabled = mtls;
  g_rpc_config->tls_algorithm = rpc_hs_algorithm_from_name(alg);
  snprintf(g_rpc_config->ca_cn, sizeof(g_rpc_config->ca_cn), "%s", sec_tls_ca_cn());
  snprintf(g_rpc_config->ca_cert, sizeof(g_rpc_config->ca_cert), "%s",
           sec_tls_cert_path("RPC_TLS_CA_CERT", CA_CERT_PATH));
  snprintf(g_rpc_config->server_cert, sizeof(g_rpc_config->server_cert), "%s",
           sec_tls_cert_path("RPC_TLS_SERVER_CERT", HOST_CERT_PATH));
  snprintf(g_rpc_config->server_key, sizeof(g_rpc_config->server_key), "%s",
           sec_tls_cert_path("RPC_TLS_SERVER_KEY", HOST_KEY_PATH));
  ```

## 三、库内部 — 消费层（从结构体字段读取）

### 1. `rdbcomm/client.h/client.c`

`client_options` 新增字段：
```c
const char *ca_cn;
const char *ca_cert;
char client_cert[512];
char client_key[512];
const char *cert_dir;
```
`client.c` 中 `rdbcomm_connect`（198-203 行）与 mTLS 路径改用字段：
```c
opts.profiles[0].ca_cert = options->ca_cert;
opts.profiles[0].ca_cn = hs_result.ca_cn;   /* 握手下发仍优先 */
/* client_cert/client_key 需按 hs_result.ca_cn 解析时用 options->cert_dir */
```
`rdbcomm_new` 拷贝 options 到 conn 持有时同步拷贝 TLS 字段。

### 2. `rdbcomm/server.h/server.c`

`server_options` 新增字段：
```c
int mtls_enabled;
uint16_t tls_algorithm;
const char *ca_cn;
const char *ca_cert;
const char *server_cert;
const char *server_key;
```
`server.c:434-439` 改为从 `conn->server->options` 读取：
```c
rpc_hs_server_config_t hs_config = {
    .mtls_required = conn->server->options.mtls_enabled,
    .algorithm = conn->server->options.tls_algorithm,
    .ca_cn = conn->server->options.ca_cn,
};
```
`rdbcommd-main.c` TLS ctx 创建（320-336）改用 `server_opts` 字段。

### 3. `rpc/rpc-config.h/rpc-io.cpp/rpc-server.cpp`

`rpc_config` 新增字段：
```c
int mtls_enabled;
uint16_t tls_algorithm;
char ca_cn[256];
char ca_cert[PATH_LEN];
char server_cert[PATH_LEN];
char server_key[PATH_LEN];
char client_cert[PATH_LEN];
char client_key[PATH_LEN];
char cert_dir[PATH_LEN];
```
- `rpc-io.cpp:85`（rpc_connect_first_stage）与 `137-141`（connect_server_session）改为从 `g_rpc_config` 读取 mtls/algorithm；mTLS 路径（153-160）用 ca_cert/cert_dir/client_cert/client_key 字段。
- `rpc-server.cpp:196-198` 改为：
  ```c
  .mtls_required = g_rpc_config->mtls_enabled,
  .algorithm = g_rpc_config->tls_algorithm,
  .ca_cn = g_rpc_config->ca_cn,
  ```
- `rpc/main.cpp` TLS ctx 创建（414-424）改用 g_rpc_config 字段。

### 4. `libs/sbt-session.{c,h}`

入口函数增加 TLS 配置入参（调用方填充），或接受 `tls_cert_client_options_t`/`tls_cert_server_options_t`：
```c
int sbt_session_client_init(rpc_hs_session_t *io, int fd,
                            const tls_cert_client_options_t *opts);
int sbt_session_server_prepare(const tls_cert_server_options_t *opts);
int sbt_session_server_accept(rpc_hs_session_t *io, int fd,
                              const tls_cert_server_options_t *opts,
                              int mtls_required, uint16_t algorithm);
```
调用方（dmsbtex/libobk）先填充 opts 再从字段读取。

### 5. `libs/timed_net_key.c`

`timed_net_key_create` 增加 TLS 配置入参或从调用方配置结构体读取（当前直接 getenv）。调用方为 fs-backup/rpc 工具，需在其 main 填充。

### 6. `dmsbtex/network.c`、`libobk/lib/logic/oracleCmdTbl.c`、`libobk/lib/sbt/libobk.c`

各自内部持有 TLS 配置字段（或接收 sbt-session 传入的 opts），`sbt_session_*` 调用改为传 opts；不再直接查 rdb-config env。

## 四、回归验证

1. `xmake build` 无新增警告。
2. `xmake test` 全部通过（含 rdb_config_test、tls_cert_test、rpc_handshake_test、rdbcomm/rpc 集成测试、tool_integration）。
3. 四工具 help 文案不变。
4. 无 CLI 工具（dmsbtex/libobk/sbt-session/timed_net_key）通过显式入参/字段生效，集成回归验证默认值行为不变。

## 五、改动文件清单

| 文件 | 改动 |
|------|------|
| `libs/rdb-config.h` | 移除 `sec_tool_tls_set_cli_overrides` 声明 |
| `libs/rdb-config.c` | 移除 cli 全局与 `set_cli_overrides`；`sec_cache_reset` 清 cli 重置 |
| `libs/tests/rdb_config_test.c` | 移除 set_cli_overrides 断言，保留纯查询断言 |
| `rdbcomm/rdbcomm-main.c` | 删除双 set_cli_overrides，合并+解析 TLS env 填入 copts |
| `rdbcomm/rdbcommd-main.c` | 删除 set_cli_overrides，合并+解析 TLS env 填入 server_opts |
| `rdbcomm/client.h/client.c` | client_options 新增 TLS 字段；connect 从字段读取 |
| `rdbcomm/server.h/server.c` | server_options 新增 TLS 字段；434-439 从字段读取 |
| `rpc/rpc-config.h` | rpc_config 新增 TLS 字段 |
| `rpc/rpc-client.cpp` | 删除 set_cli_overrides，合并填入 g_rpc_config |
| `rpc/main.cpp` | 删除 set_cli_overrides，合并填入 g_rpc_config |
| `rpc/rpc-io.cpp` | 85/137-141/153-160 从 g_rpc_config 读取 |
| `rpc/rpc-server.cpp` | 196-198 从 g_rpc_config 读取 |
| `libs/sbt-session.{c,h}` | 入口增加 TLS 配置入参 |
| `libs/timed_net_key.c` | 增加 TLS 配置入参 |
| `dmsbtex/network.c` | 显式 TLS 字段；sbt_session 调用传 opts |
| `libobk/lib/logic/oracleCmdTbl.c` | 显式 TLS 字段；sbt_session 调用传 opts |
| `libobk/lib/sbt/libobk.c` | 显式 TLS 字段；sbt_session 调用传 opts |

## 六、验收映射

- AC-1 ← 一（set_cli_overrides 移除、纯查询不变）
- AC-2 ← 二（四工具合并逻辑，CLI 覆盖生效、未指定回退默认）
- AC-3 ← 三.1/三.2/三.3（结构体传值，server.c/rpc-server/rpc-io/client.c 从字段读取；消费点不再 getenv）
- AC-4 ← 三.4/三.5/三.6（sbt-session/timed_net_key/dmsbtex/libobk 显式入参/字段生效）
- AC-5 ← 四.1/四.2（build + test 全通过）