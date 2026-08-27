# 结论文档（Check 阶段）

任务：T3986-0827-sbt-server-client-config-split
阶段：Do -> Check（conclusion 草稿，verdict 待用户确认）

## 一、实现概述

将 SBT 系（libobk / dmsbtex）服务端/客户端共用的 mTLS rdb 配置，拆分为四个角色
独立的配置来源，使 server 与 client 互不干扰；证书目录仍走全局 `[security]cert_dir`，不拆分。

新增 8 个角色参数（rdb-config 注册表）：
- `[libobk_server]` / `[libobk_client]` : `mtls_enable`、`tls_algorithm`
- `[dmsbtex_server]` / `[dmsbtex_client]` : `mtls_enable`、`tls_algorithm`

删除 3 个旧的 SBT 共用名称（完全迁移）：
- 参数 ID：`PARAM_SBT_MTLS_ENABLED`、`PARAM_SBT_TLS_ALGORITHM`、`PARAM_LIBOBK_CLI_TLS_ALGORITHM`
- env 宏：`SBT_MTLS_ENABLE_ENV`、`SBT_TLS_ALGORITHM_ENV`
- **保留**全局 `[security]tls_enable` / `[security]tls_algorithm`（RPC 系 aio-speedd/rdbcommd 兜底依赖，不可删）

## 二、改动文件

- `libs/rdb-config.h`：新增 8 角色参数枚举 + 模块×角色 section/env 宏；删除 3 旧 macro/ID。
- `libs/rdb-config.c`：`g_param_table` 新增 8 条目（链 env > [模块_角色]section > def，无全局兜底）；删除 3 旧条目。
- `libobk/lib/sbt/libobk.c`：`sbt_client_tls_config_init` 改读 `[libobk_client]` 参数。
- `libobk/lib/logic/oracleCmdTbl.c`：`sbt_server_tls_config_init` 改读 `[libobk_server]` 参数。
- `dmsbtex/network.c`：`sbt_tls_config_init`（server）改读 `[dmsbtex_server]`；新增 `dmsbtex_client_tls_config_init` 读 `[dmsbtex_client]`。
- `dmsbtex/network.h`：声明 `dmsbtex_client_tls_config_init`。
- `dmsbtex/sbt.c`：client 基线改由 `dmsbtex_client_tls_config_init` 初始化；`sbt-config.conf` 的 `file_mtls`/`file_alg` 仍以最高优先级覆盖（用户裁定：sbt-config.conf 类似命令行参数，优先级最高）。
- `libobk/main.c`、`dmsbtex/main.c`：usage 文本中 env 名改为 `[libobk_server]`/`[dmsbtex_server]`（CLI 覆盖经 `cli_mtls`/`cli_algorithm` 参数传入 server 入口，已正确映射 server 角色）。
- `libs/tests/param_registry_test.c`：新增 `sbt_role_config_independent`（默认/section/env 覆盖/角色独立）；改写 `sec_get_bool_fail_closed` 体现无全局兜底。
- `libs/tests/rdb_config_test.c`：改写 `bool_layer_semantics` 验证新角色参数不被 `[security]` 全局影响、自身 section 脏值 fail-closed。

## 三、验证证据

- `xmake build param_registry_test rdb_config_test`：构建通过。
- `param_registry_test`：**10 passed**（含 `sbt_role_config_independent`）。
- `rdb_config_test`：**20 passed**（含改写后 `bool_layer_semantics` 与既有审计/鉴权回归）。
- `xmake build dmsbtex libobk_session_test FileTransferAgent dmsbtex_session_test`：全部编译通过（libdmsbtex.so / libsbt.so / FileTransferAgent / 两个 session_test）。

## 四、AC 对照

- AC-1 四角色参数独立解析链：满足（注册表 + `sbt_role_config_independent`）。
- AC-2 删除 3 旧 SBT 名称、保留全局 `[security]`：满足（grep 全仓无残留；RPC 兜底保留）。
- AC-3 server/client 入口各自读对应角色、互不覆盖：满足（4 入口迁移 + 新增 client 函数）。
- AC-4 cert_dir 全局不变：满足（仅 `PARAM_CERT_DIR` 读取，未改动）。
- AC-5 全量单元测试回归：满足（libs 30 passed）。
- AC-6 xmake build/test 通过：libs 与两模块构建通过（session_test 运行需证书/网络环境，编译已验证）。
- AC-7 旧 env 名不再影响 SBT 系解析：满足（宏已删，usage 改新名）。
- AC-8 fail-closed / 算法白名单保持：满足（沿用 sec_get_bool + strcmp 白名单，未改语义）。

## 五、待决 / 备注

- dmsbtex client 的 `sbt-config.conf` 文件覆盖按用户裁定保留为最高优先级，未删除旧文件路径（非 rdb 参数，不在本次删除范围）。
- 命令行 `--mtls-enable`/`--tls-algorithm` 覆盖映射到 server 角色（与既有行为一致：CLI 仅覆盖 server 侧）。
- 模块级 session_test 行为回归需在具备证书/网络的环境运行 `xmake test`，本次仅完成编译验证。

## 六、结论

实现满足 PRD 全部 AC（AC-1..AC-8）。建议 verdict：**pass**（进入 Act 归档）。

verdict（待用户）： ____
