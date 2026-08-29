# T0398 结论（Check 阶段）

- 任务：T0398-0827-s3tools-rdb-config-integrate
- 标题：s3tools（s3file + s3mount）接入 rdb-config 注册表并统一错误上抛
- 阶段：Do 完成，待用户 verdict

## 1. 目标与范围

将 s3tools 下 s3file / s3mount 自带的 `ini_parse` + `atoi` 直接解析 rdb config 的代码，
统一迁移到 `libs/rdb-config` 的集中式参数注册表（T0397 已为 rpc/fs-backup/rdbcomm/libs/dmsbtex/libobk 完成）。
消除"绕过注册表"的解析入口，使全部工具的配置读取走同一套 env>段>默认 解析链与
`rdb_cfg_errcode_t` + `detail` 错误上抛契约。

范围经 grill 确认：s3file 与 s3mount **两者都接入**；`verify_ssl` 默认保持不启用（0）；
缺 rdb.conf（ENOENT）**容忍**回落默认（与 fs-backup 一致）。

## 2. 实现概述

### 2.1 注册表新增 8 条目（libs/rdb-config.c `g_param_table`）
- `[s3file]cache_path`：STR，默认 `/tmp/s3-cache/`，maxlen 4095，fail-closed
- `[s3file]gmssl`：BOOL，默认 0
- `[s3file]parallel`：INT，默认 8，min 1，fail-closed
- `[s3mount]verify_ssl`：BOOL，默认 0
- `[s3mount]cache_path`：STR，默认 `/tmp/s3-cache/`
- `[s3mount]cache_capacity`：INT，默认 NULL（**必填**），min 1，fail-closed
- `[s3mount]log_path`：STR，默认 `/opt/aio/logs/tools/s3mount/`
- `[s3mount]fuse_mount_point`：STR，默认 `/fuse/`

对应 `libs/rdb-config.h` 新增 section/key 宏与 `RDB_DEFAULT_S3_*` 默认宏。
`env_name=NULL`：无 key 级环境变量覆盖层，符合历史用 `RDB_CONFIG` 定位配置文件路径的语义。

### 2.2 s3tools 代码迁移
- `s3tools/s3file/config.cpp`、`s3tools/s3mount/config.cpp`：
  重写为经 `sec_get_int/bool/str` 取注册表值，配置错误以 `rdb_cfg_errcode_t` + `detail`
  上抛，调用方直印 `r.detail`（移除旧的 `atoi` + 模糊 `err_msg` 归因）。
  删除自带的 `ini_parse` / `do_parse_config` / `*_check_config`。
- `config.h` 删除已失效的 `*_check_config` 声明。
- `s3file/main.cpp:403`、`s3mount/fuse.cpp:232` 调用方改用新签名
  `int init_config(const char *config_file, char *err_msg, int len)`，并
  `!= 0 → ErrorLog + exit`（fail-closed）。
- `s3tools/s3file/xmake.lua`、`s3tools/s3mount/xmake.lua` 增加 `add_deps("rdb-config")`。

### 2.3 审查发现并修复的关键 bug（重要）
原实现在 `parse_config` 返回 `ENOENT` 时**直接 `return 0`**，跳过了后续 `sec_get` 的必填校验。
后果：s3mount 的 `cache_capacity` 为必填（无默认），但缺文件时 `rc=0` 且 `cache_capacity`
静默为 0——必填语义被"文件允许不存"绕过（历史要求必填启动会失败）。
修复：`s3file/config.cpp:107`、`s3mount/config.cpp:20` 改为
"ENOENT 仅容忍解析错误、不提前返回，继续走 `sec_get_*`"；必填字段缺失仍以
`INT_MISSING` fail-closed 拒绝。修复后 s3mount 缺文件 → `rc=-1`（与历史一致）。

### 2.4 冗余防御清理
字符串取值原多了 `!r.value || r.value[0]=='\0'` 判断，已核实 `sec_walk_str` 内部
`v && v[0]` 已把空串当无值，回落默认/MISSING，故删除冗余，仅判 `!r.ok`。

### 2.5 技术债清理（用户明确要求）
删除 `s3tools/s3file/config.h`、`s3tools/s3mount/config.h` 中失效的 `DEFAULT_CACHE_DIR` /
`DEFAULT_LOG_DIR` / `DEFAULT_MOUNT_POINT` 等死宏（全 s3tools 内无任何引用），
使 `rdb-config.h` 的 `RDB_DEFAULT_S3_*` 成为默认值唯一来源。

## 3. 验证证据（AC）

- `xmake build s3file s3mount`：链接 rdb-config，编译通过。
- 新增 `s3tools/s3file/tests/config_test.cpp`、`s3tools/s3mount/tests/config_test.cpp`
  （经 `includes("tests")` 接入 `xmake test`），覆盖：
  - 正常读取各字段；
  - 缺省回落（仅必填/无关段 → 可选字段取默认）；
  - **缺文件（ENOENT）容忍**：s3file 无必填 → `rc=0`；s3mount 因 `cache_capacity` 必填 → `rc=-1`；
  - 必填缺失（文件中无键）→ fail-closed 拒绝；
  - 非法类型：非 0/1 布尔、非整数 INT 均拒绝。
- `xmake test` 全量 **48/48 通过**（含新增 2 个 s3 配置单测）。

## 4. 遗留 minor（非阻断，建议后续）
- `s3file parallel` 为 `int`，由 `sec_get_int`（long, max=LONG_MAX）转 int，极端超大值有截断风险；
  可选收紧 `max` 到 `INT_MAX` 或在调用处校验。当前无实际影响。
- `s3mount cache_capacity` 为 `uint64_t`，由 long 转，因 `min=1` 保证非负，安全。

## 5. 结论与 verdict

实现完成、单测与全量回归均绿，且审查中暴露的"ENOENT 绕过绕过必填校验"真实 bug 已修复，
技术债（重复默认值宏）已清理。建议 **verdict = confirmed**（通过）。

verdict 待用户确认。
