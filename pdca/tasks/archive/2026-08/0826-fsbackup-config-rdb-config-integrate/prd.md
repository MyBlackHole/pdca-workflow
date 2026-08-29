# PRD — fs-backup 接入集中式 rdb config

## 问题陈述
fs-backup（fsdeamon / fsclient）目前用**自有** `do_parse_config` + `ini_parse` + `atoi` 解析
`[fsdaemon]` / `[fsclient]` 段（见 `fs-backup/fsdeamon/config.cpp:15`、`fs-backup/fsclient/config.cpp:15`）。
这与集中式 `rdb config`（`libs/rdb-config.c`）产生两处不一致：

1. **重复解析器**：同一份 `/opt/aio/cfg/rdb.conf` 已由 `init_config(NULL)` 解析进 rdb-config 全局
   `_kv_store`，fs-backup 却用第三套解析器再解析一遍。
2. **宽松解析语义漂移**：`atoi` 对脏值静默当作 `0`/关；而集中式 `config_get_int` 采用严格整数解析
   （非法值回退默认并 stderr 告警），与全仓 fail-closed 配置语义不一致。

rdbcomm、libobk 已完全接入（直接走 `sec_get_*` / store，无独立解析器），fs-backup 是残留的
"混合 + 旁路" 之一（见 mTLS 审查 F-series 的延伸发现）。

## 目标
fs-backup 的配置读取统一接入集中式 rdb config 的**参数注册表**（`libs/rdb-config.c` 的
`PARAM_*` + `sec_get_*`），删除自有 inih/atoi 解析器，与 rdbcomm/libobk 对齐，实现
"统一管理参数"（env > 工具段 > 默认，fail-closed）。

## 用户故事
- 作为维护者：希望 fs-backup 与 rdbcomm/libobk 复用同一套集中式配置解析，避免重复实现与解析语义漂移。
- 作为安全审计者：希望所有工具的配置解析都遵循 fail-closed 严格语义。

## 范围
- 修改：`fs-backup/fsdeamon/config.cpp(.h)`、`fs-backup/fsclient/config.cpp(.h)`。
- 行为：init / reload 时从 `_kv_store` 读取 `[fsdaemon]`/`[fsclient]`；保留 `*_check_config` 取值范围校验。
- 不涉及：dmsbtex `sbt.conf` 路径、s3tools / xbsa、rpc / rdbcomm / libobk（已接入）。

## 方案
1. `fsdeamon_init_config` / `fsclient_init_config` 移除 `fsdeamon_parse_config` / `fsclient_parse_config`
   中的 `ini_parse(do_parse_config)` 分支与自有 `do_parse_config` 函数。
2. 在 `libs/rdb-config.c` 参数注册表 `g_param_table` 新增 fs-backup 的 9 个 `PARAM_*` 项
   （fsdaemon: check_data/debug/keepalive/retry；fsclient: check_data/retry/keepalive/read_timeout/parallel），
   并在 `rdb-config.h` 的 `config_param_id_t` 枚举与工具/环境宏区登记对应 ID 与 `*_ENV` 名。
   layer2 指向既有 `[fsdaemon]`/`[fsclient]` 段，类型 BOOL/INT，默认值与历史一致；
   layer3（全局兜底）置 NULL（此类为工具级调参，非全仓安全策略）。
3. fs-backup 改为经 `sec_get_bool(PARAM_*)` / `sec_get_int(PARAM_*)` 读取（统一解析链 env>工具段>默认）。
   **BOOL 字段（`check_data`/`debug`）须先用 `int` 临时量承接 `sec_get_bool` 的返回值**：`sec_get_bool`
   对非法值返回 `-1`（fail-closed），而 `Config.check_data`/`debug`/`CliConfig.check_data` 是 `bool`，
   直接赋值会把 `-1` 截断成 `1` 从而绕过 fail-closed，故显式预校验 `v < 0` 即拒绝启动。
   INT 字段沿用 `sec_get_int`（宽松语义：非法值回退默认，与历史 `atoi` 一致）。
4. 保留 `*_check_config` 取值范围校验（`keepalive`/`retry`/`read_timeout`/`parallel` >= 0 等）；
   BOOL 的 0|1 约束由注册表严格解析保证。
5. **保留配置传播副作用**：读取后照常调用 `set_rpc_check_data` / `set_rpc_keepalive_interval` /
   `set_rpc_retry`（及 fsclient 的 `set_rpc_read_timeout` / `set_rpc_parallel`），否则 rpc 侧收不到值。
6. reload 路径：`unix_server.cpp` 的 `process_reload_cmd` 已调用 `fsdeamon_parse_config`；其中
   经 `parse_config(config_path)`（集中式）刷新 `_kv_store` 后重新 `sec_get_*`，实现热加载。
   `parse_config` 整体刷新 store，但本进程内 rpc 已在 `set_rpc_init_config` 时把 `sec_*` 缓存进自有 struct，无副作用。
7. 删除不再使用的 `do_parse_config`、`<ini.h>` 包含，补充 `#include "rdb-config.h"`；
   fsclient 本地 `static parse_config` 改名 `fsclient_parse_config` 以避免与 rdb-config 全局 `parse_config` 重名冲突。

## Seam 分析
### 声明的测试接缝
- seam: `fs-backup/fsdeamon/tests/config_test.cpp` -> `fs-backup/fsdeamon/config.cpp`
  （链接 `rdb-config` + `set_rpc_*` 桩；构造临时 rdb.conf 含 `[fsdaemon]`，调用 `fsdeamon_init_config`
   后断言 check_data/debug/keepalive/retry 取值，并断言桩记录的 `set_rpc_*` 调用值；含失败用例 check_data=2 拒绝启动、缺省回退默认）。
- seam: `fs-backup/fsdeamon/tests/param_test.c` -> `libs/rdb-config.c`
  （仅链 `rdb-config`；验证全部 9 个新 `PARAM_*` 经注册表正确解析：env>工具段>默认、BOOL 非法值
   fail-closed 返回 -1、缺省回退、env 覆盖）。
- 注：fsclient 的 `fsclient/config.cpp` 因 `config.h` 引入 `fs_service_proto.h` 重依赖，未单独链接单测；
  其 `sec_get_*` 读取与 `set_rpc_*` 传播由与 fsdeamon 完全同构的代码 + `fs-cli` 构建 + 注册表单测共同覆盖。

## 实现/测试决策
- 采用 development 路径：先写失败测试，再改实现。
- 测试构造临时 rdb.conf（含 `[fsdaemon]`/`[fsclient]`）并调用 `fsdeamon_init_config` / `sec_get_*` 读取断言。
- 在 `fs-backup/fsdeamon/tests/xmake.lua` 注册 `fsdeamon_config_test`（链 config.cpp + rdb-config + 桩）
  与 `rdb_param_test`（仅链 rdb-config）两个目标。

## 风险与缓解
- **RISK A（`atoi`→严格解析语义差）**：`sec_get_int`（INT 宽松，非法值回退默认 + stderr 告警）
  与 `sec_get_bool`（BOOL 严格，非法值返回 `-1` 即拒绝启动）整体上较 `atoi` 更严格。
  如 `check_data=2` 将由历史"视作真"变为"启动失败"（fail-closed）；`keepalive=3600s` 带单位则回退默认 30。
  这是有意的强化，但 Do 前须确认生产 rdb.conf 中 `[fsdaemon]`/`[fsclient]` 的数值均为严格整数（无单位后缀）。
  无法从仓库验证，列为部署侧确认项（AC-8）。
- **RISK B（reload 刷新全局 store）**：热加载改用 `parse_config(config_file)` 会整体刷新 `_kv_store`；
  本进程内 rpc 已在 `set_rpc_init_config` 时把 `sec_*` 缓存进自有 struct，故无副作用，Do 阶段实证。
- **RISK C（测试前置）**：`fsdeamon_init_config` 读 `_kv_store`，单测须先 `init_config(testfile)` 装载
  store，再调用 `fsdeamon_init_config(testfile)`，否则读到空 store 全默认、测不出解析逻辑。

## 验收标准
- [x] AC-1: fsdeamon 删除自有 `do_parse_config` 与 `ini_parse` 调用，改经注册表 `sec_get_*` 读取 `[fsdaemon]` 的 check_data/debug/keepalive/retry（新增 `PARAM_FSDEAMON_*`）。
- [x] AC-2: fsclient 同样删除自有解析器，改经 `sec_get_*` 读取 `[fsclient]` 段（新增 `PARAM_FSCLIENT_*`，含 check_data/retry/keepalive/read_timeout/parallel）。
- [x] AC-3: 构造 rdb.conf 含合法 `[fsdaemon]`/`[fsclient]` 值，init 后 `g_pConfig` 各字段与配置一致（`fsdeamon_config_test` + `rdb_param_test` 实证）。
- [x] AC-4: 构造脏值（如 check_data=2）经 `sec_get_bool` 返回 -1 触发 fail-closed 拒绝启动；INT 脏值（如 keepalive=3600s）回退默认并 stderr 告警（`*_check_config` 仍生效）。
- [x] AC-5: 全仓构建通过（`xmake build fsdeamon fsclient` 及新增 `fsdeamon_config_test` / `rdb_param_test`）；新增用例全部 PASS。
- [x] AC-6: rdbcomm/libobk 行为不受影响（未修改其配置代码），集中式 `_kv_store` 来源（`init_config`）未变更；既有 `rdb_config_test` / `param_registry_test` 仍全 PASS（新增参数项未导致枚举移位）。
- [x] AC-7: 保留 `set_rpc_check_data`/`set_rpc_keepalive_interval`/`set_rpc_retry`（及 fsclient 的 `set_rpc_read_timeout`/`set_rpc_parallel`）调用；`fsdeamon_config_test` 以桩记录 `set_rpc_*` 调用值，验证传播与配置一致。
- [ ] AC-8: 部署侧确认项——生产 rdb.conf 的 `[fsdaemon]`/`[fsclient]` 数值均为严格整数（RISK A）；若发现非严格值，先于发布前反馈评估（告警+回退默认是否符合预期）。

## 范围外
- dmsbtex `sbt.conf` 配置路径（本期不做）。
- s3tools / xbsa 配置接入（后续议题）。
- rpc 非安全段合并（低优，后续）。

## 备注
- `_kv_store` 由 `init_config(NULL)` 解析中央 `/opt/aio/cfg/rdb.conf` 装载；fs-backup 的 `config_file`
  （`RDB_CONFIG` env 或 `DEFAULT_RDB_CONFIG_PATH`）与 `init_config` 来源一致，读取安全。
- 参考实现：rdbcomm `server.c` / libobk `oracleCmdTbl.c` 均直接走 `sec_get_*`/store，无独立解析器。
