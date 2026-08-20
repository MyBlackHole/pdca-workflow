# 修正 TLS CLI 覆盖时序：启动即加载默认值，参数解析后存在则覆盖

## 问题陈述

- **现状**: TLS 配置参数分散且隐式：
  1. CLI 覆盖机制（`cli_mtls_set/cli_mtls_enabled/cli_algorithm` static 全局 + `sec_tool_tls_set_cli_overrides`，libs/rdb-config.c:216-218,325-338）被塞进 rdb-config，由四个工具 main 在 `args_process` 后调用。rdb-config 因此持有"工具 CLI 覆盖"这一**工具特有状态**，违背"自己的东西自己持有与销毁"的职责边界。
  2. 证书路径等 TLS 内部参数（`RPC_TLS_CA_CERT`/`RPC_TLS_SERVER_CERT`/`RPC_TLS_SERVER_KEY`/`RPC_TLS_CLIENT_CERT`/`RPC_TLS_CLIENT_KEY`/`RPC_TLS_CERT_DIR`/`RPC_TLS_CA_CN`）在各消费点（client.c/server.c/rpc-io/rpc-server/sbt-session/timed_net_key/dmsbtex/libobk）**隐式 getenv/查询**，未显式存在于调用方结构体。
- **目标**: 
  1. rdb-config 只保留基础 key/value 通用查询（env/config/master 优先级解析），不持有工具状态。
  2. 工具特有的 CLI 参数解析、检测条件、覆盖合并归各工具自身实现。
  3. **全部 TLS 内部参数显式存在于各调用方结构体字段**（client_options/server_options/g_rpc_config/各库入口配置），库模块从结构体字段读取，不再隐式 getenv。
- **差距**: CLI 覆盖状态存放在 rdb-config 而非工具；证书路径等 TLS 参数隐式查询而非结构体显式持有；库内部直接读 env 而非调用方传入的字段。

## 依赖关系与模块职责

### 配置查询方（读取 TLS 配置）

| 调用方 | 位置 | 当前查询 | 承载结构体 | 所需显式字段 |
|--------|------|---------|-----------|-------------|
| rdbcomm 客户端 | `rdbcomm/client.c:201-203` | getenv RPC_TLS_CA_CERT/CLIENT_CERT | `client_options` | mtls_enabled/tls_algorithm（已有）+ ca_cn/ca_cert/client_cert/client_key/cert_dir |
| rdbcommd 服务端 | `rdbcomm/server.c:434-439` | 查 rdb-config | `server_options` | mtls_enabled/tls_algorithm/ca_cn/ca_cert/server_cert/server_key（新增） |
| rpc 客户端连接 | `rpc/rpc-io.cpp:85,137` | 查 rdb-config | `g_rpc_config` | mtls_enabled/tls_algorithm/ca_cn/ca_cert/client_cert/client_key/cert_dir（新增） |
| rpc 服务端 | `rpc/rpc-server.cpp:196-198` | 查 rdb-config | `g_rpc_config` | mtls_enabled/tls_algorithm/ca_cn/ca_cert/server_cert/server_key（新增） |
| sbt-session | `libs/sbt-session.c:27-52` | 查 rdb-config | 函数入参 | 新增 tls 配置结构体入参或扩展入参 |
| timed_net_key | `libs/timed_net_key.c:24-45` | 查 rdb-config | 函数入参 | 新增 tls 配置入参 |
| dmsbtex | `dmsbtex/network.c:75-133` | 查 rdb-config | network 内部配置 | 新增 tls 配置字段 |
| libobk | `libobk/lib/logic/oracleCmdTbl.c:45-65`、`libobk/lib/sbt/libobk.c:78-80` | 查 rdb-config | 内部配置 | 新增 tls 配置字段 |

### 覆盖注入方（CLI 工具 main，各自独立进程，自己持有覆盖状态）

| 工具 | main | 覆盖状态字段 | 最终值承载 |
|------|------|-------------|-----------|
| rdbcomm | `rdbcomm/rdbcomm-main.c` | `options_t.cli_mtls_set/cli_mtls_enabled/cli_algorithm` | `client_options`（含全部 TLS 字段） |
| rdbcommd | `rdbcomm/rdbcommd-main.c` | `options.cli_*` | `server_options`（含全部 TLS 字段） |
| aio-speed | `rpc/rpc-client.cpp` | `g_rpc_args.cli_*` | `g_rpc_config`（含全部 TLS 字段） |
| aio-speedd | `rpc/main.cpp` | `g_rpc_config.cli_*` | `g_rpc_config`（含全部 TLS 字段） |

### 职责划分

- **rdb-config**（基础配置层）：只提供基础 key/value 通用查询——env/config/master 优先级解析（`sec_tool_tls_enabled/algorithm` 纯查询、`sec_tls_*` 系列）。**不持有**工具 CLI 覆盖状态，不提供覆盖注入接口。
- **CLI 工具 main**（注入层）：解析 `--mtls-enable`/`--tls-algorithm` 到自己的结构体字段；解析 TLS 证书 env 到结构体字段；合并默认值与 CLI 覆盖（CLI 存在则覆盖）；把**全部最终值**填入自己持有的配置结构体。
- **库/模块调用方**（消费层）：从工具传入的配置结构体字段读取最终值，不再隐式 getenv/查 rdb-config cli 状态。无 CLI 的工具（dmsbtex/libobk/sbt-session/timed_net_key）在自己的配置结构体/入参中显式持有 TLS 参数。

### 时序依赖链

```
CLI 工具进程:
  args_process()（解析 CLI 到 cli_* 字段）
      │
  main 解析 TLS env（RPC_TLS_* 系列）到结构体字段
      │
  main 合并: 最终值 = CLI 存在 ? CLI : env/config 查询
      │
  填入工具配置结构体（client_options / server_options / g_rpc_config）
      │
  库模块从结构体字段读取（server.c / rpc-server / rpc-io / client.c）
```

当前 4 个工具通过 `set_cli_overrides` 把覆盖注入 rdb-config，库内部再查 rdb-config——间接依赖。重构后为**直接传值**：工具解析/合并 → 结构体 → 库读取。

## 解决方案

- **rdb-config**: 移除 `cli_mtls_*` static 全局与 `sec_tool_tls_set_cli_overrides`；`sec_tool_tls_enabled/algorithm` 保持纯查询（无 cli 分支）；`sec_cache_reset` 不再重置 cli 状态。保留 `sec_tls_cert_path`/`sec_tls_client_cert_paths` 作为基础路径解析工具（工具 main 用它解析后填入结构体，消费点不再直接调用）。
- **工具层**: 四个 main 各自解析 CLI + TLS env，合并后填入自己持有的配置结构体全部 TLS 字段。
- **库内部**: `rdbcomm/client.c`、`rdbcomm/server.c`、`rpc/rpc-server.cpp`、`rpc/rpc-io.cpp` 改为从结构体字段读取；`sbt-session.c`/`timed_net_key.c`/`dmsbtex/network.c`/`libobk` 增加显式 TLS 配置字段/入参。
- 不改变 CLI 参数名、取值规则、help 文案。

四个工具 main 统一合并模式：

```c
/* rdbcomm-main.c 示例 */
int mtls_enabled = sec_tool_tls_enabled(RDBCOMM_TOOL_SECTION,
                                        RDBCOMM_MTLS_ENABLE_ENV);
if (opts.cli_mtls_set)
    mtls_enabled = opts.cli_mtls_enabled;
const char *alg = sec_tool_tls_algorithm(RDBCOMM_TOOL_SECTION,
                                         RDBCOMM_TLS_ALGORITHM_ENV);
if (opts.cli_algorithm)
    alg = opts.cli_algorithm;
opts.copts.mtls_enabled = mtls_enabled;
opts.copts.tls_algorithm = rpc_hs_algorithm_from_name(alg);
opts.copts.ca_cn = sec_tls_ca_cn();
opts.copts.ca_cert = sec_tls_cert_path("RPC_TLS_CA_CERT", CA_CERT_PATH);
opts.copts.cert_dir = sec_tls_cert_path("RPC_TLS_CERT_DIR", DEFAULT_CERT_DIR);
snprintf(opts.copts.client_cert, sizeof(...), "%s",
         sec_tls_cert_path("RPC_TLS_CLIENT_CERT", ""));
snprintf(opts.copts.client_key, sizeof(...), "%s",
         sec_tls_cert_path("RPC_TLS_CLIENT_KEY", ""));
```

## Seam 分析

### 测试接缝

- 测试边界在 `libs/rdb-config.c` 公共 API：确认 `sec_tool_tls_enabled/algorithm` 无 cli 分支、纯查询行为不变；`sec_tls_cert_path/client_cert_paths` 基础解析保留。
- 工具侧合并逻辑在四个 main：通过 help/解析测试与集成测试验证 CLI 覆盖生效。
- 库内部读取改为结构体字段：通过工具集成测试验证最终值正确传递。
- 外部依赖隔离：无新增外部依赖，仅配置解析与 env。

### 声明的测试接缝

- seam: `libs/tests/rdb_config_test.c` -> `sec_tool_tls_*` 纯查询行为（移除 set_cli_overrides 断言）
- seam: `rdbcomm/rdbcomm-main.c`、`rdbcomm/rdbcommd-main.c`、`rpc/rpc-client.cpp`、`rpc/main.cpp` -> 合并逻辑与 TLS 字段填充
- seam: `rpc/tests/tool_integration.cpp`、`rdbcomm/tests/tool_integration.c` -> 四工具 help 与 CLI 集成（沿用 T0322 接缝）
- seam: `libs/tests/tls_cert_test.c`、`libs/tests/rpc_handshake_test.c` -> 库内部从结构体字段读取的回归

### 验收可测性

- 每个 AC 有明确 pass/fail 信号（运行测试/构建/grep）。

## 用户故事

1. 作为工具进程，我希望 TLS 覆盖状态与全部 TLS 参数由自己持有，以便生命周期清晰、不依赖 rdb-config 的隐式全局状态。
2. 作为运维，我希望 `--mtls-enable`/`--tls-algorithm` 在参数解析后覆盖默认值，以便单次调用临时调整。
3. 作为维护者，我希望全部 TLS 参数通过结构体显式传给库模块，以便职责边界清晰、时序可推理、无隐式 env 依赖。

## 实现决策

**新增/修改的模块**：`libs/rdb-config.{c,h}`（移除 cli 覆盖机制）、四个工具 main（自持覆盖并填充结构体）、`rdbcomm/server.h/server.c`、`rdbcomm/client.h/client.c`、`rpc/rpc-config.h/rpc-io.cpp/rpc-server.cpp`、`libs/sbt-session.{c,h}`、`libs/timed_net_key.c`、`dmsbtex/network.c`、`libobk/lib/logic/oracleCmdTbl.c`、`libobk/lib/sbt/libobk.c`、`libs/tests/rdb_config_test.c`。

**各结构体新增字段**：

```c
/* rdbcomm/client.h client_options 新增 */
const char *ca_cn;
const char *ca_cert;
char client_cert[512];
char client_key[512];
const char *cert_dir;

/* rdbcomm/server.h server_options 新增 */
int mtls_enabled;
uint16_t tls_algorithm;
const char *ca_cn;
const char *ca_cert;
const char *server_cert;
const char *server_key;

/* rpc/rpc-config.h rpc_config 新增 */
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

**sbt-session/timed_net_key/dmsbtex/libobk**：为入口函数增加 TLS 配置结构体入参（或复用 `tls_cert_client_options_t`/`tls_cert_server_options_t`，由调用方填充全部字段）。

**技术澄清**：

- 各工具 main 合并逻辑：`最终值 = CLI 存在 ? CLI 值 : sec_tool_tls_* 查询值`。CLI 参数解析/校验（0/1、合法算法名）已在 args_process 完成（T0322 已实现），合并仅读取解析结果。
- 工具 main 用 `sec_tls_cert_path`/`sec_tls_ca_cn`/`sec_tls_client_cert_paths` 解析 TLS env 到结构体字段；消费点不再直接调用这些查询。
- 库内部读取点（client.c/server.c/rpc-io/rpc-server）改为从结构体字段读取；其中 rpc-io.cpp 的 `rpc_connect_first_stage`（fd 级，仅协商不建 mTLS）与 `rpc_get_time`（仅 time）本就无需实际 mTLS 值，仍可读默认值或结构体字段。
- rdbcomm-main.c 的 time 子命令分支（599-608）与常规分支（609-611）的 `set_cli_overrides` 双调用收敛为**一次合并**。
- 不改变 CLI 参数名、取值规则、help 文案。
- `sec_cache_reset` 保留（测试重置用），仅移除 cli 状态重置。

**架构决策**：CLI 覆盖状态与全部 TLS 参数归工具/调用方持有，通过各结构体显式字段传给库模块；rdb-config 只做基础查询。记入 ADR。

**数据模型变更**：无持久化数据变更。

**API 合约**：`sec_tool_tls_set_cli_overrides` 移除；`client_options`/`server_options`/`rpc_config` 新增字段；`sbt_session_*`/`timed_net_key_*` 入参扩展；`sec_tool_tls_enabled/algorithm` 签名不变。

## 测试决策

- 仅测外部行为：通过公共 API 构造场景，断言默认值先行、CLI 覆盖生效、结构体字段正确填充与读取。
- 被测模块：`libs/rdb-config.{c,h}`、四个工具 main、`client.c`/`server.c`/`rpc-io.cpp`/`rpc-server.cpp`、`sbt-session.c`/`timed_net_key.c`。
- 现有先例：`rdb_config_test.c` 断言风格、`tool_integration` 集成风格。

## 验收标准

- [ ] AC-1: 运行 rdb-config 单元测试，得到 `sec_tool_tls_enabled/algorithm` 纯查询行为不变（env/config/master 优先级正确），`sec_tool_tls_set_cli_overrides` 已移除（编译/链接通过）。
- [ ] AC-2: 运行四个工具 help 与参数解析测试，`--mtls-enable`/`--tls-algorithm` 解析后合并生效；未指定时行为与默认值一致；非法值错误信息不变。
- [ ] AC-3: 运行工具集成测试，最终生效值通过结构体（client_options/server_options/g_rpc_config）传给库模块；server.c/rpc-server/rpc-io/client.c 从字段读取正确；证书路径 env（RPC_TLS_*）不再在消费点隐式查询。
- [ ] AC-4: 运行 sbt-session/timed_net_key/dmsbtex/libobk 相关测试与集成，TLS 配置通过显式入参/字段生效。
- [ ] AC-5: 运行 `xmake build` 与 `xmake test`，全部测试通过；不修改 TLS 证书加载、握手协议、profile 模型。

## 范围外

- 不改变 TLS 证书加载、握手协议、profile 模型。
- 不改变 CLI 参数名、取值规则、help 文案。
- 不改变 `sec_*` 其它配置接口（sec_tls_enabled/auth/audit/ciphersuites 等）。
- 不引入新的全局锁或配置热重载。

## 备注

- 与 T0322（0819-tool-mtls-cli-args-v2）为后续关系：T0322 引入 CLI 参数与覆盖机制，本任务修正其职责归属（覆盖状态与 TLS 参数归调用方）。
- 与 T0332（0820-tls-cert-refactor）为后续关系：T0332 确立 profile 模型与 ca_cn 握手下发，本任务收敛 TLS 参数显式传递。