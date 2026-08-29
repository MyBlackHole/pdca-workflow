---
schema: pdca.spec/v1
id: T0397-0827-rdb-config-error-propagation
title: rdb config 配置错误以异常号+异常详情向上传递，移除内部打印
scenario_type: development
parent: T0396
---

## 问题陈述

当前 `libs/rdb-config` 的错误传播存在两类缺陷，导致上层工具打印的启动错误信息不明确、不可机读：

1. **无异常号、无详情**：`sec_get_int`/`sec_get_bool`/`sec_get_str` 失败时仅返回裸 `-1`/`NULL`，
   不携带"为什么失败"（非整数 / 越界 / 超长 / 缺失）。调用方（rpc/fs-backup/rdbcomm）只能自造
   模糊文案，例如统一写 `invalid %s value (expect >=%ld)`——当真实原因是"非整数"时该文案会误导为
   "小于下限"，运维无法据此判断对错。
2. **内部直接打印**：`config_get_int`（脏值回退路径，rdb-config.c:91）与 `CONFIG_KV_MAX` 截断
   （rdb-config.c:25）直接向 `stderr` 打印。这些打印与调用方自己的日志无关联、不可控，既污染上层
   输出，又使"同一错误被打印两次/信息错位"。

目标：用**稳定的异常号（`rdb_cfg_errcode_t`）+ 自包含的异常详情（`detail`）** 取代内部打印与裸返回，
   让调用方以异常号做分类、以详情打印明确可读的启动错误，且 rdb-config 内部不再自行向 stderr 打印。

## 解决方案

在 `libs/rdb-config` 引入结构化错误传播：

- **异常号枚举**（rdb-config.h）：
  ```c
  typedef enum {
    RDB_CFG_OK = 0,
    RDB_CFG_ERR_UNKNOWN_PARAM,        /* id 无效 */
    RDB_CFG_ERR_INT_INVALID,          /* 非整数（parse_strict_int 失败） */
    RDB_CFG_ERR_INT_OUT_OF_RANGE,      /* 越界（sec_test_int_bounds 失败） */
    RDB_CFG_ERR_INT_MISSING,          /* 缺失且无默认（sec_get_int 返回 -1） */
    RDB_CFG_ERR_BOOL_INVALID,         /* 非 "0"/"1" */
    RDB_CFG_ERR_STR_TOO_LONG,         /* 超长（sec_test_str_bounds 失败） */
    RDB_CFG_ERR_STR_MISSING,          /* 缺失且无默认（sec_get_str 返回 NULL） */
    RDB_CFG_ERR_FILE_OPEN,            /* 配置文件打不开 */
    RDB_CFG_ERR_INI_PARSE,            /* ini 解析失败（ini_parse<0） */
    RDB_CFG_ERR_TRUNCATED,            /* warning 级：KV 超 CONFIG_KV_MAX 被截断 */
  } rdb_cfg_errcode_t;
  const char *rdb_cfg_strerror(rdb_cfg_errcode_t code); /* 异常号 -> 人类文本 */
  /* parse_config/init_config 同样返回 result 结构体（与 sec_get_* 一致，全参数化无线程局部） */
  typedef struct {
    int ok;                 /* 1 成功 / 0 失败 */
    rdb_cfg_errcode_t code; /* RDB_CFG_OK / ERR_FILE_OPEN / ERR_INI_PARSE */
    char detail[160];       /* 人类可读详情（含路径/原因） */
  } rdb_cfg_parse_result;
  rdb_cfg_parse_result parse_config(const char *config_file);
  rdb_cfg_parse_result init_config(const char *config_file);
  ```
- **result 结构体**（替代裸返回值，rdb-config.h）：
  ```c
  typedef struct {
    int ok;                 /* 1 成功 / 0 失败 */
    long value;             /* 成功时的 INT 值（long，与 parse_strict_int 一致，避免截断） */
    rdb_cfg_errcode_t code; /* 异常号；成功时恒为 RDB_CFG_OK */
    char detail[160];       /* 异常详情（自包含，随返回值拷贝，无生命周期问题） */
  } rdb_cfg_int_result;

  typedef struct {
    int ok;                 /* 1 成功 / 0 失败 */
    int value;              /* 成功时的 BOOL 值（0/1） */
    rdb_cfg_errcode_t code; /* 异常号；成功时恒为 RDB_CFG_OK */
    char detail[160];
  } rdb_cfg_bool_result;

  typedef struct {
    int ok;
    const char *value;      /* 成功时指向 store/默认串（生命周期同 _kv_store） */
    rdb_cfg_errcode_t code;
    char detail[160];
  } rdb_cfg_str_result;

  rdb_cfg_int_result  sec_get_int(config_param_id_t id);
  rdb_cfg_bool_result sec_get_bool(config_param_id_t id);
  rdb_cfg_str_result  sec_get_str(config_param_id_t id);
  ```
  `detail` 内容示例（须标注取值来源 env/段，便于定位）：
  `env RPC_TOOL_RETRY='abc' is not a valid integer`、
  `[aio-speedd]retry=0 out of range [min=1,max=2147483647]`、
  `[aio-speedd]check_data='2' is not 0/1`、
  `[aio-speedd]fsbackup_dev_path length 5000 exceeds max 4095`、
  `[aio-speedd]fsbackup_dev_path has no value and no default`、
  `unknown param id 123`。
  `sec_walk_*` 须记录 `raw` 实际出自 env 还是 layer2/layer3，并在 `detail` 中写明对应来源
  （env 名 / `[段]键`），避免调用方再猜测。
- **移除内部打印，改诊断回调**：
  - 删除 `config_get_int` 的 `fprintf(stderr,...)`（rdb-config.c:91），保留"脏值回退默认"语义。
  - `CONFIG_KV_MAX` 截断（rdb-config.c:25）不再直接打印，改为触发可注册诊断回调：
    ```c
    typedef void (*rdb_cfg_diagnostic_cb)(rdb_cfg_errcode_t code,
                                          const char *detail, void *ctx);
    void rdb_cfg_set_diagnostic_cb(rdb_cfg_diagnostic_cb cb, void *ctx); /* 默认 NULL=静默 */
    ```
    默认静默；需要可观测性的调用方可注册回调（如转发到自身日志）。rdb-config 内部不再有任何直接
    `stderr` 错误/告警打印。
- **parse_config 细化**：先用 `access()` 区分"文件打不开"（RDB_CFG_ERR_FILE_OPEN）与
  `ini_parse<0`（RDB_CFG_ERR_INI_PARSE）；返回 `rdb_cfg_parse_result`，`code` 为异常号，
  `detail` 填含具体路径/原因的人类可读文本（即异常详情），调用方据 `code` 分类、`detail` 打印，
  全参数化、无线程局部。

## Seam 分析

### 测试接缝
- seam: libs/tests/rdb_config_test.c -> libs/rdb-config.c
- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c
- seam: rpc/tests/rpc_param_test.c -> libs/rdb-config.c （注册表解析）
- seam: rpc/tests/rpc_config_test.cpp -> rpc/rpc-config.cpp
- seam: fs-backup/fsdeamon/tests/config_test.cpp -> fs-backup/fsdeamon/config.cpp
- seam: fs-backup/fsdeamon/tests/param_test.c -> libs/rdb-config.c

### 声明的测试接缝
- seam: libs/tests/rdb_config_test.c -> libs/rdb-config.c
- seam: libs/tests/param_registry_test.c -> libs/rdb-config.c
- seam: rpc/tests/rpc_param_test.c -> libs/rdb-config.c
- seam: rpc/tests/rpc_config_test.cpp -> rpc/rpc-config.cpp
- seam: fs-backup/fsdeamon/tests/config_test.cpp -> fs-backup/fsdeamon/config.cpp
- seam: fs-backup/fsdeamon/tests/param_test.c -> libs/rdb-config.c

### 验收可测性
全部 AC 可由上述单测套件断言（错误码数值、detail 子串、调用方失败分支、诊断回调触发/静默、回归全绿）。

## 用户故事

- 作为 rpc/fs-backup 启动逻辑，我希望读取配置失败时拿到"异常号 + 明确详情"，从而打印
  `[aio-speedd]retry=0 out of range [min=1,max=...]` 而非模糊的 `invalid retry value`，便于运维定位。
- 作为 rdb-config 库，我不应自行向 stderr 打印，错误应完全由调用方决定如何记录。

## 实现决策

- 异常号用独立枚举（非 errno），数值稳定、与业务解耦，可作运维查询号。
- 向上传递用 result 结构体经**出参指针**传递，且函数返回 `int`（即 result.ok，便于 `if (sec_get_int(id,&r))` 判成功），用户裁定：所有 `sec_get_*`/`parse_config`/`init_config` 改为
  `int sec_get_int(config_param_id_t id, rdb_cfg_int_result *out)` 等形式（out 填充 `ok`/`value`/`code`/`detail`，返回 `out->ok`）。代价是所有调用方必须同步改造（无部分兼容）。涉及模块（经全仓核对）：rpc（rpc-config.cpp/rpc-client.cpp）、fs-backup（fsdeamon/config.cpp、fsclient/config.cpp）、rdbcomm（rdbcomm-main.c/rdbcommd-main.c）、libs（logger.c/timed_key.c）、**dmsbtex（network.c）**、**libobk（lib/logic/oracleCmdTbl.c、lib/sbt/libobk.c）** 及相关单测。fail-closed 语义（非法 BOOL 维持开启、越界/超长拒绝启动、缺失回落默认）保持不变。
- INT 非整数取值（如 `keepalive=30s`）：维持 T0396 的 fail-closed 拒绝（`result.ok=0`、`code=RDB_CFG_ERR_INT_INVALID`），**不回退默认**；越界仍按 `invalid_policy` 回落/拒绝。注册表描述中"非法值回退默认"已更正为"非整数 fail-closed 拒绝"。
- `parse_config`/`init_config` 同样以出参指针返回 `rdb_cfg_parse_result`（`code`+`detail`），与 `sec_get_*` 的 result 结构体风格一致；全仓**不使用线程局部**，异常号+详情一律经 result 出参传递。`config_get_int` 仅被单测使用（遗留宽松路径），本次移除其 stderr 打印、保留回退语义，不引入 result 改造。
- `detail[160]` 由调用方栈上持有的 result 结构体承载，自包含、无悬垂指针风险。
- **调用方迁移范式（防 fail-closed 回归，务必遵循）**：
  - BOOL（如 audit/keycheck）：旧 `if (!sec_get_bool(id))` 改为
    `rdb_cfg_bool_result r; sec_get_bool(id, &r); if (r.ok && r.value == 0) { /* 关闭 */ }`；
    `!r.ok`（非法值）**不进入关闭分支** ⇒ 维持开启（fail-closed）。
  - INT（如 keepalive/retry）：旧 `int v = sec_get_int(id); if (v < 0) fail;` 改为
    `rdb_cfg_int_result r; sec_get_int(id, &r); if (!r.ok) { /* 打印 r.detail 并拒绝启动 */ } else { use (int)r.value; }`。
  - STR 安全字段（tls_algorithm/cert_dir/dev_path）：旧 `const char *s = sec_get_str(id);` 改为
    `rdb_cfg_str_result r; sec_get_str(id, &r); if (!r.ok) { /* 打印 r.detail 并拒绝启动 */ } else { s = r.value; }`；
    **`!r.ok`（超长/缺值无默认）必须拒绝启动**，不得把 `r.value==NULL` 当默认用（消除原 NULL 歧义）。
  - `parse_config`/`init_config`：旧 `if (parse_config(p,err,len)<0)` 改为
    `rdb_cfg_parse_result r; parse_config(p, &r); if (!r.ok) { /* 打印 r.detail，r.code 分类 */ }`。

## 测试决策

- 注册表单测新增：每个异常号一条用例，断言 `code` 数值与 `detail` 含段/键/取值/原因子串；截断场景断言
  `parse_config` 返回 `code==RDB_CFG_ERR_TRUNCATED` 且 `detail` 含截断信息（无全局诊断回调）。
- 调用方单测（rpc_config_test / fsdeamon config_test）改为基于 result 判断，并断言失败分支打印的
  `err_msg` 含明确详情（如 `out of range [min=1`）。
- 回归：既有取值/回落/失败-closed 用例全部改用 result 后保持原断言。

## 验收标准

- [ ] AC-1: 定义 `rdb_cfg_errcode_t` 枚举（含 RDB_CFG_OK/UNKNOWN_PARAM/INT_INVALID/INT_OUT_OF_RANGE/INT_MISSING/BOOL_INVALID/STR_TOO_LONG/STR_MISSING/FILE_OPEN/INI_PARSE/TRUNCATED）并提供 `rdb_cfg_strerror()` 映射，数值稳定。
- [ ] AC-2: `sec_get_int`/`sec_get_bool`/`sec_get_str` 返回 result 结构体（`ok`/`value`/`code`/`detail[160]`）；失败时 `code` 取值自 `RDB_CFG_ERR_*` 且 `detail` 精确（含取值来源 env/段、键、取值、原因，如 `out of range [min=1,max=...]`/`is not a valid integer`/`length N exceeds max M`/`has no value and no default`）；成功时 `ok=1`、`code=RDB_CFG_OK`。
- [ ] AC-3: 移除 `config_get_int` 的 `fprintf(stderr,...)`；`CONFIG_KV_MAX` 截断不再内部打印，改为经 `parse_config` 返回的 `rdb_cfg_parse_result` 暴露（`ok=1`、`code=RDB_CFG_ERR_TRUNCATED`、`detail` 描述截断条数/文件）；rdb-config 内部不再有直接 stderr 错误/告警打印（无全局诊断回调、无线程局部）。
- [ ] AC-4: `parse_config`/`init_config` 返回 `rdb_cfg_parse_result`，区分 `RDB_CFG_ERR_FILE_OPEN` 与 `RDB_CFG_ERR_INI_PARSE`，`detail` 填含具体原因的异常详情，异常号经 `code` 返回（全参数化、无线程局部）。
- [ ] AC-5: 全部调用方（rpc/rpc-config.cpp、rpc/rpc-client.cpp、fs-backup fsdeamon+fsclient config.cpp、rdbcomm-main.c、rdbcommd-main.c、libs/logger.c、libs/timed_key.c、**dmsbtex/network.c**、**libobk/lib/logic/oracleCmdTbl.c、libobk/lib/sbt/libobk.c**）改用 result 的 `ok`/`code`/`detail` 判断；调用 `parse_config`/`init_config` 处读取 `r.code`+`r.detail` 打印明确错误；**须直接打印 `r.detail`（已含来源/键/取值/原因）而非自造模糊文案**；不再出现 `invalid %s value` 类笼统表述；fail-closed 语义不变。
- [ ] AC-6: 全部单测（rdb_config_test/param_registry_test/rpc_param_test/rpc_config_test/logger_test/fs-backup fsdeamon config_test+param_test）改用 result 并全绿；新增用例覆盖各异常号（INT_INVALID/INT_OUT_OF_RANGE/BOOL_INVALID/STR_TOO_LONG/STR_MISSING/FILE_OPEN/INI_PARSE）与 detail 断言、诊断回调触发与默认静默。
- [ ] AC-7: libs/rpc/fs-backup/rdbcomm/dmsbtex/libobk 全量构建零错误，无回归。
- [ ] AC-8: 部署侧确认（延迟，不阻塞 confirmed）：运维可据异常号查询错误含义；发布前复核生产 rdb.conf 以使错误可定位。

## 范围外

- 不改动 `_kv_store` 存储结构与 ini 解析器本身（仅细化错误分类）。
- 不为每个工具引入独立的错误码命名空间（统一用 `rdb_cfg_errcode_t`）。
- 不处理运行时（非启动配置）错误的传播，仅限配置加载/读取路径。
- 日志框架接入（如统一日志库）不在本次范围，诊断回调仅提供钩子。

## 备注

- 因 result 结构体改变 `sec_get_*` 签名，本任务须同步改造全部调用方方可编译通过，属机械性但跨模块。
- 与 T0394/T0395/T0396 同属"rdb config 参数注册表统一"主线：T0396 已下沉范围校验，本任务补齐
  "错误可定位"一环。
- **INI_PARSE 详情精度限制**：inih 的 `ini_parse` 不返回出错行号，`RDB_CFG_ERR_INI_PARSE` 的 `detail`
  仅能到文件级（含路径/errno），无法精确定位到行；如需行级定位需替换 ini 解析器，不在本次范围。
- **诊断回调非线程安全**：`rdb_cfg_set_diagnostic_cb` 为全局单回调，配置加载为单线程初始化，可接受；
  多线程并发加载配置的场景不在本次范围。
- `config_get_int` 为遗留宽松函数（脏值回退默认），仅被单测引用；本次仅移除其 stderr 打印、保留
  回退语义，不改造为 result（避免扩大面），后续清理可移除。
