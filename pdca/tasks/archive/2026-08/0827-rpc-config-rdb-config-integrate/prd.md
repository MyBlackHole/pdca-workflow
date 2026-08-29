# T0395 — rpc：接入集中式 rdb config，移除独立 atoi 解析器

> 关联：T0394（fs-backup 接入 rdb config 参数注册表，已完成归档）。
> 目标：消除 rpc 自有的 `do_parse_config`+`ini_parse`+`atoi` 配置解析器，
> 将 rpc 可调参数统一接入 `libs/rdb-config.c` 参数注册表，沿用 T0394 的
> fail-closed 严格解析模式（BOOL 截断陷阱已沉淀于
> `knowledge/rdb-config/wire-tool-config-to-registry.md`）。

## 1. 背景与现状

- `rpc/rpc-config.cpp` 的 `rpc_parse_config` 调用 `do_parse_config`（`ini_parse` +
  `atoi`），从 `g_section_name` 指定段（默认 `AIO_SPEED_TOOL_SECTION="aio-speed"`，
  aio-speedd 经 `rpc_set_section_name` 改为 `"aio-speedd"`）读取
  `check_data/debug/keepalive/parallel/read_timeout/retry/fsbackup_dev_path`，
  写入 `rpc_config *g_rpc_config`。
- `rpc_set_section_name` 生产唯一调用点为 `rpc/main.cpp:363`
  （`AIO_SPEEDD_TOOL_SECTION`）；fs-backup 不调用，依赖 `set_rpc_*` 推送
  （T0394 已令其从 `[fsdaemon]` 读取后推送）。
- `rpc_config` 其余字段（mtls_enabled/audit_enabled/auth_enabled/tls_algorithm/
  cert_dir）已走 registry，本次不动。
- 与 T0394 前的 fs-backup 同构：重复的、宽松的 `atoi` 解析，缺乏 env 覆盖、
  安全层治理与 fail-closed。

## 2. Grill 结论（已 captured）

| # | 议题 | 裁定 |
|---|------|------|
| Q1 | 统一范围 | **aio-speedd + 默认 aio-speed 两个段**均注册到注册表 |
| Q2 | 动态段名 | **固定单一键、废弃 `rpc_set_section_name` 的动态可变段名** |
| Q3 | dev_path（字符串） | 注册为 `CFG_TYPE_STR` 参数，经 `sec_get_str` 读取 |
| Q4 | 测试 | 扩展 `rpc_config_test` + 新增独立注册表单测 |

### 张力调和与自我审查修正（已定稿）
Q1（覆盖 [aio-speedd] + [aio-speed] 两段）与 Q2（废弃动态段名、固定单一键）的
**最终一致方案**（经自我审查修正）：

- **每个 tunable 注册单条 PARAM**，`layer2_section=AIO_SPEEDD_TOOL_SECTION`、
  `layer2_key=<key>`、`layer3_section=AIO_SPEED_TOOL_SECTION`、`layer3_key=<key>`。
  经 `sec_get_*` 一次读取即实现 **env > [aio-speedd] > [aio-speed] > 默认** 的优先级链。
  → 既“覆盖两段”（Q1），又彻底消除运行时可变段名（Q2），且**无回归**。
- **关键验证（防回归）**：fs-backup 仅经 `set_rpc_*` 推送 `check_data/keepalive/retry`
  （fsdeamon）或再 +`read_timeout/parallel`（fsclient），**从不推送 `dev_path`**。
  旧逻辑里 `dev_path` 由 rpc 从默认段 `[aio-speed]` 经 atoi 读取；本方案中
  `[aio-speedd]` 缺失时 `sec_get_str` 回落到 `layer3=[aio-speed]`，`dev_path` 来源与
  现状一致，**不产生回归**。其余被推送字段由 `[fsdaemon]` 推送覆盖，优先级亦不变。
- **回归对比表**（fs-backup 进程内 `g_rpc_config` 最终值）：
  | 字段 | 旧（atoi [aio-speed] → set_rpc_* 推送） | 新（sec_get_* layer2=aio-speedd→layer3=aio-speed → set_rpc_* 推送） |
  |------|------|------|
  | check_data/keepalive/retry(+read_timeout/parallel) | [fsdaemon] 推送值 | [fsdaemon] 推送值（推送覆盖，不变） |
  | dev_path | [aio-speed] atoi 值 | [aio-speed]（layer3 回落）值，不变 |
  | mtls/audit/auth… | registry（不变） | registry（不变） |

> 说明：原“rpc 固定只读 AIO_SPEEDD_*、另注册一套 AIO_SPEED_*（共 14 条）”方案因上述
> `dev_path` 回归风险被否决，收敛为 7 条 PARAM + layer3 回落。

## 3. 实施设计

### 3.1 注册表新增参数（`libs/rdb-config.c` / `.h`）
在 `config_param_id_t` 枚举与 `g_param_table` 新增 **7 条** PARAM（沿用 T0394 命名风格），
每条 `layer2=[aio-speedd]`、`layer3=[aio-speed]`，实现两段优先级回落：

- `PARAM_RPC_CHECK_DATA` — BOOL，默认 0
- `PARAM_RPC_DEBUG` — BOOL，默认 0
- `PARAM_RPC_KEEPALIVE` — INT，默认 30（`DEFAULT_KEEPALIVE_INTERVAL`）
- `PARAM_RPC_PARALLEL` — INT，默认 4
- `PARAM_RPC_READ_TIMEOUT` — INT，默认 120000
- `PARAM_RPC_RETRY` — INT，默认 3（`DEFAULT_RETRY`）
- `PARAM_RPC_DEV_PATH` — STR，默认 `DEFAULT_DEV_PATH`

每条字段：`layer2_section=AIO_SPEEDD_TOOL_SECTION`（`"aio-speedd"`）、
`layer2_key=<key>`、`layer3_section=AIO_SPEED_TOOL_SECTION`（`"aio-speed"`）、
`layer3_key=<key>`、`env_name`（如 `RPC_TOOL_CHECK_DATA_ENV`，于 `rpc-config.h` 新增）、
`type`、`def`。`sec_get_*` 依 env > layer2 > layer3 > def 解析。

> 命名采用 `PARAM_RPC_*`（而非 `PARAM_AIO_SPEEDD_*`/`PARAM_AIO_SPEED_*` 两套），
> 因为单条 PARAM 已通过其 layer2/layer3 同时覆盖两段，无需两套。

### 3.2 `rpc/rpc-config.cpp` 改造
- 删除 `do_parse_config`、`ini_parse` 及其文件作用域 `tmp` 中间结构与 `atoi` 分支。
- `rpc_parse_config` 中 tunable 读取改为（单条 PARAM，经 layer2/layer3 回落，
  无需关心段名）：
  - BOOL（`check_data`/`debug`）：先以 `int` 临时量经 `sec_get_bool(PARAM_RPC_*)`
    取得，**无效值（-1）触发 fail-closed** → `rpc_init_config`/`rpc_parse_config`
    响亮返回 -1；再赋给 `bool` 字段（规避 `bool` 截断 `-1`→`1` 绕过校验，见知识库）。
  - INT（`keepalive`/`parallel`/`read_timeout`/`retry`）：`sec_get_int`（宽松，
    非法回落默认）。
  - STR（`fsbackup_dev_path`）：`sec_get_str(PARAM_RPC_DEV_PATH)` 写入
    `g_rpc_config->fsbackup_dev_path`。**STR 不走 fail-closed**（见 T0394 纠偏：
    F4 误报，dev_path 缺失应回落 `DEFAULT_DEV_PATH`）。
- `mtls/audit/auth/tls_algorithm/cert_dir` 既有 registry 读取保持不变。
- 全部 tunable 现统一经 `sec_get_*`，**移除所有 `atoi` 调用**。

### 3.3 段名 API 处理（Q2）
- `rpc_set_section_name` 改为 **deprecated no-op**（保留签名以兼容 `rpc/main.cpp:363`
  与既有测试编译，加注释标注废弃）；`g_section_name` 固化为常量
  `AIO_SPEEDD_TOOL_SECTION`；`rpc_get_section_name` 返回该常量（供 `rpc_show_config`
  打印段头，无需改动输出语义）。
- `rpc/main.cpp:363` 的 `rpc_set_section_name(AIO_SPEEDD_TOOL_SECTION)` 调用可保留
  （no-op）或一并删除；建议删除并去除该语句以减少误导。

### 3.4 复用与一致性
- 沿用 T0394 的 `sec_get_*` 调用约定、`CONFIG_PARAM_COUNT` 自动计数、编译期段名长度断言。
- fs-backup 的 `set_rpc_*` 推送模型保持不变（T0394 已落地），rpc 库读取 AIO_SPEEDD 段
  与推送互不冲突（推送后到）。

## 验收标准

- [ ] AC-1: `rpc-config.cpp` 中不再存在 `ini_parse`/`atoi` 对 tunable 的解析；`do_parse_config` 整体删除。
- [ ] AC-2: 注册表新增 7 条 PARAM（`PARAM_RPC_*`，每条 `layer2=[aio-speedd]`、`layer3=[aio-speed]`），编译期 `g_param_table` 长度断言通过。
- [ ] AC-3: 给定含 `[aio-speedd]` 的 rdb.conf，`check_data/debug/keepalive/parallel/read_timeout/retry/fsbackup_dev_path` 经 `sec_get_*` 正确解析并写入 `g_rpc_config`；默认值与现状一致。当 `[aio-speedd]` 缺失该键时，回落读取 `[aio-speed]`（layer3），保证嵌入方沿用既有 `[aio-speed]` 段来源，**无回归**。
- [ ] AC-4: ENV 层优先于段值（如 `RPC_TOOL_KEEPALIVE_ENV` 覆盖 `[aio-speedd] keepalive`）。
- [ ] AC-5: BOOL 字段（`check_data`/`debug`）仅接受 `0`/`1`（经 `sec_parse_strict_bool`），遇其它值触发 fail-closed：`rpc_init_config`/`rpc_parse_config` 返回 -1；INT 字段遇非法值回落默认；STR `dev_path` 缺失/非法回落 `DEFAULT_DEV_PATH`（不 fail-closed）。
- [ ] AC-6: `rpc_set_section_name` 为 no-op（或已删除）；`rpc_get_section_name` 返回 `aio-speedd`；`rpc_show_config` 输出语义不变。
- [ ] AC-7: `xmake build rpc` 构建通过；既有 `rpc_config_test` 及新增用例全部 PASS；新增独立注册表单测验证 7 条新 `PARAM_RPC_*` 解析链（env>layer2>layer3>默认、BOOL fail-closed、STR 默认回落）无回归；`rdb_config_test`/`param_registry_test` 无回归。
- [ ] AC-8: 部署侧确认项——生产 rdb.conf 中 `[aio-speedd]`/`[aio-speed]` 段布尔 tunable（`check_data`/`debug`）须使用 `0`/`1`；数值 tunable 须为严格整数，不得依赖旧 atoi 宽松语义。若存在旧写法，列入发布前待办并登记延迟证据。

## 5. 测试接缝（Seam）声明

- `rpc/tests/rpc_config_test.cpp` → `rpc/rpc-config.cpp`（扩展既有 `[aio-speedd]` 段用例，
  新增 check_data/debug/parallel/read_timeout/retry/dev_path 经 `sec_get_*` 的断言、
  BOOL fail-closed、默认值、**layer3 回落**（在 `[aio-speedd]` 缺失时将值置于 `[aio-speed]`
  验证读取）、env 覆盖；原 `rpc_set_section_name` 调用改为 no-op 兼容或不调用；更新第 126
  行注释中对 `do_parse_config` 的提及）。
- `rpc/tests/rpc_param_test.c` → `libs/rdb-config.c`（新增独立注册表单测，仅链 rdb-config，
  验证 7 条 `PARAM_RPC_*` 的解析链：env > layer2([aio-speedd]) > layer3([aio-speed]) >
  def、BOOL fail-closed、STR 回落默认；xmake 新增 `rpc_param_test` 目标，仿 T0394 的
  `rdb_param_test`）。

## 6. 范围与依赖

- **范围**：仅 rdb config 接入；`sbt.conf` 不属本次范围（与 T0394 一致）。
  mtls=0 语义维持“不强制”（可选），不改。
- **依赖**：`libs/rdb-config.c`（registry + `sec_get_*`）由 T0394 已落地，可直接复用。
- **关联任务**：T0394（已完成）。本任务不改动 fs-backup 既有 `set_rpc_*` 推送逻辑。
