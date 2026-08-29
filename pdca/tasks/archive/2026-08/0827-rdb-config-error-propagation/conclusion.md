---
schema: pdca.asset/v1
id: T0397-0827-rdb-config-error-propagation
phase: check
source_ids: [E-T0397-DO-001, E-T0397-CONV, E-T0397-AC8]
---

## 上下文

T0394/T0395/T0396 已将 fs-backup 与 rpc 配置统一接入集中式 rdb config 注册表，并补齐 INT 边界与
fail-closed 语义。但取值失败时，注册表层仅以 `-1`/`NULL` 返回值（或旧的 3 参 `err_msg` 填充）向外传递，
调用方只能看到 `invalid retry value` 一类笼统文案，无法稳定定位"哪一段/哪个键/取了什么值/为什么错"；
且 `config_get_int` 与 `CONFIG_KV_MAX` 截断仍在库内部向 stderr 打印，错误归因被库吞掉。本任务把配置错误
以**独立异常号 `rdb_cfg_errcode_t` + 明确异常详情 `detail`** 经 result 结构体（出参指针，函数返回 `int`
即 ok）向上传递，移除库内 stderr 打印，使上层打印信息明确、可机读、可运维查询。

## 假设与结果

- **AC-1** 定义 `rdb_cfg_errcode_t` 枚举（RDB_CFG_OK/UNKNOWN_PARAM/INT_INVALID/INT_OUT_OF_RANGE/
  INT_MISSING/BOOL_INVALID/STR_TOO_LONG/STR_MISSING/FILE_OPEN/INI_PARSE/TRUNCATED）并提供
  `rdb_cfg_strerror()` 稳定数值映射：`PASS`（ev-diff 隐含，E-T0397-DO-001 构建通过）。
- **AC-2** `sec_get_int`/`sec_get_bool`/`sec_get_str` 改为 `int sec_get_*(id, rdb_cfg_*_result *out)`，
  失败时 `code` 取自 `RDB_CFG_ERR_*`、`detail` 精确含取值来源（env/[段]键）、取值、原因
  （`out of range [min=1,max=8]`/`is not a valid integer`/`length N exceeds max M`/`has no value and no default`）；
  成功 `ok=1`、`code=RDB_CFG_OK`：`PASS`（E-T0397-DO-001 中 `error_propagation_result_struct` 断言
  `rb.code==RDB_CFG_ERR_BOOL_INVALID` 且 `strlen(rb.detail)>0`、`pr2.code==RDB_CFG_ERR_FILE_OPEN`）。
- **AC-3** 移除 `config_get_int` 的 `fprintf(stderr,...)`；`CONFIG_KV_MAX` 截断不再内部打印，改为经
  `parse_config` 返回 `rdb_cfg_parse_result`（`ok=1`、`code=RDB_CFG_ERR_TRUNCATED`、`detail` 描述截断条数/文件）；
  库内不再有 stderr 错误/告警打印，无全局诊断回调、无线程局部：`PASS`（E-T0397-DO-001）。
- **AC-4** `parse_config`/`init_config` 改为 `int parse_config(const char*, rdb_cfg_parse_result *out)`，
  区分 `RDB_CFG_ERR_FILE_OPEN`（access 失败）与 `RDB_CFG_ERR_INI_PARSE`（ini_parse 失败），`detail` 填含
  具体原因（路径 + strerror），异常号经 `code` 返回，全参数化、无线程局部：`PASS`（E-T0397-DO-001）。
- **AC-5** 全部调用方（rpc/rpc-config.cpp、rpc/rpc-client.cpp、fs-backup fsdeamon+fsclient config.cpp、
  rdbcomm-main.c、rdbcommd-main.c、libs/logger.c、libs/timed_key.c、**dmsbtex/network.c**、**libobk/lib/logic/
  oracleCmdTbl.c、libobk/lib/sbt/libobk.c**）改用 result 的 `ok`/`code`/`detail` 判断，直印 `r.detail`
  （已含来源/键/取值/原因）而非自造模糊文案；fail-closed 语义不变（非法 BOOL 维持开启、越界/超长拒绝启动、
  缺失回落默认）：`PASS`（E-T0397-DO-001 全模块构建零错误 + rpc_config_test/fsdeamon_config_test 全绿）。
- **AC-6** 全部单测（rdb_config_test 20、param_registry_test 9、rpc_param_test 6、logger_test 11、
  rpc_config_test 9、fs-backup fsdeamon config_test、rdb_param_test）改用 result 并全绿；新增
  `error_propagation_result_struct` 覆盖 `BOOL_INVALID`/`FILE_OPEN` 的 `code`+`detail` 断言：
  `PASS`（E-T0397-DO-001）。其中 `int_invalid_falls_back_to_default` 已据裁定改为
  `int_invalid_is_fail_closed`（非整数维持 fail-closed 返回 -1，不回退默认）。
- **AC-7** libs/rpc/fs-backup/rdbcomm/dmsbtex/libobk 全量构建零错误，无回归：`PASS`
  （E-T0397-DO-001：tools + 全部测试 target + rdbcommd/dm-ftp/aio-speedd/aio-speed/fsdeamon/fs-cli 均 build ok）。
- **AC-8** 部署侧确认（运维据异常号可查含义、发布前复核生产 rdb.conf）为延迟项、不阻塞 confirmed：
  本任务仅实现库与调用方的异常号+详情上抛，不执行部署动作：`PARTIAL/延迟`（E-T0397-AC8）。

## 分析

- **异常号与详情解耦**：`rdb_cfg_errcode_t` 为独立枚举（非 errno），数值稳定、可作运维查询号；
  `detail[160]` 随调用方栈上 result 结构体持有，自包含、无悬垂指针、无线程局部。
- **出参指针 + int 返回**：经用户最终裁定，`sec_get_*`/`parse_config`/`init_config` 以 `int` 返回 `ok`
  （等价于 `result.ok`）便于 `if (sec_get_int(id,&r))` 判成功，result 细节经出参指针回传；代价是全部调用方
  同步改造（无部分兼容），已覆盖 rpc/fs-backup/rdbcomm/libs/dmsbtex/libobk 全模块。
- **移除内部打印、错误归属调用方**：`config_get_int` 仅在单测使用的遗留宽松路径移除 `fprintf`；
  `CONFIG_KV_MAX` 截断不再静默或打印，改经 `parse_config` 返回的 `code=RDB_CFG_ERR_TRUNCATED` 暴露，
  上层据 `detail` 决定如何记录——错误完全由调用方负责，符合"库不自行打印"的边界。
- **fail-closed 不变**：INT 非整数（如 `keepalive=30s`）维持 T0396 的 fail-closed 拒绝（`INT_INVALID`，
  不回退默认）；注册表描述中"非法值回退默认"已更正为"非整数 fail-closed 拒绝"，消除误导。
- **调用方迁移范式已固化**：BOOL 仅 `value==0` 才关闭（非法值维持开启）、安全 STR `!r.ok` 必须拒绝启动、
  调用方直印 `r.detail`，已落到生产代码与单测断言。

## 适用边界

- 安全敏感 STR（tls_algorithm/cert_dir/dev_path）`!r.ok` 视为致命错误，调用方不得把 `r.value==NULL` 当默认；
  缺失回落默认仅适用于"有 def 且非安全校验"的普通参数。
- 生产部署侧（AC-8）须确认运维可据异常号解释错误、发布前复核生产 rdb.conf，使错误可定位。

## 下一轮建议

- 若需为某调用方补充"错误上抛到进程退出码/日志结构化字段"，可直接消费 `r.code`+`r.detail`，
  无需改动 rdb-config 库。
- 后续新增工具接入注册表时，按此 result 出参范式取值即可获得统一错误归因。
