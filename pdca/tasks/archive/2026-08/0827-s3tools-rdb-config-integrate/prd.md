# s3tools 接入 rdb-config 注册表 — 规格文档（草案）

## 问题陈述

- **现状**: s3tools 的 `s3file`/`s3mount` 通过 `getenv(RDB_CONFIG)` 回落 `DEFAULT_RDB_CONFIG_PATH`（与 rdb-config 同源 `libs/cfg_path.h`）读取**同一份 rdb config 文件**，却用自带 `ini_parse`+`atoi` 直接解析 `[s3file]`/`[s3mount]` 段，这些键**未登记进 `libs/rdb-config.c` 注册表**。
- **目标**: 与 fs-backup/rpc（T0394–T0397）一致，s3tools 也经统一注册表取值，配置错误以 `rdb_cfg_errcode_t` 异常号 + `detail` 明确上抛，移除内部 `atoi`+`err_msg` 模糊归因。
- **差距**: ① s3tools 配置键游离于注册表之外；② 错误归因无统一异常号/详情；③ `verify_ssl` 默认保持不启用（0，与历史一致），仅统一错误上抛，不翻安全默认（用户裁定优先兼容）；④ 缺 rdb.conf 文件历史语义"容忍回落默认"，经核实为全局约定（fs-backup 已对 `RDB_CFG_ERR_FILE_OPEN && errno==ENOENT` 容忍），s3tools 保持容忍回落默认。

## 解决方案

沿用 T0394–T0397 已建立的接入范式：
1. 在 `libs/rdb-config.c` 的 `g_param_table` 登记 `[s3file]`、`[s3mount]` 参数（`*_ENV` 宏化、layer2 指向各自段）。
2. s3tools 删除自带 `ini_parse`+`do_parse_config`+`atoi`，改经 `sec_get_int`/`sec_get_bool`/`sec_get_str` 取注册表值；`s3file_init_config`/`s3mount_init_config` 内部先 `parse_config(rdb-config)` 再 `sec_get_*`。
3. 失败经 `rdb_cfg_*_result` 的 `ok/code/detail` 判断，调用方直印 `r.detail`（移除 `snprintf(err_msg,...)` 模糊文案）。fail-closed 语义与历史 `check_config` 对齐。
4. 单测迁移：新增/改造 `s3file`/`s3mount` 配置单测，断言取值、缺省回落、缺字段拒绝、非整数/非布尔拒绝。

## Seam 分析

### 测试接缝
- 链接 `rdb-config` + s3tools 配置结构体桩，构造临时 rdb.conf 调用 `s3file_init_config`/`s3mount_init_config`，断言取值与拒绝路径。
- 复用 `libs/tests` 的注册表单测覆盖 env>段>默认 解析链（新增 s3file/s3mount 键用例）。

### 声明的测试接缝
- seam: `s3tools/s3file/tests/s3file_config_test.cpp` -> `s3tools/s3file/config.cpp`
- seam: `s3tools/s3mount/tests/s3mount_config_test.cpp` -> `s3tools/s3mount/config.cpp`
- seam: `libs/tests/param_registry_test.c` -> `libs/rdb-config.c`

### 验收可测性
- 每个键的缺省回落、缺字段拒绝、类型非法拒绝均可独立构造临时 rdb.conf。

## 待登记参数清单（来自源码核对）

- `[s3file]` `cache_path`: str, 默认 `DEFAULT_CACHE_DIR`, 空→拒绝
- `[s3file]` `gmssl`: bool(0/1), 默认 0
- `[s3file]` `parallel`: int, 默认 8, min 1
- `[s3mount]` `verify_ssl`: bool, 默认 0（**默认不启用，与历史一致；用户裁定保留**）
- `[s3mount]` `cache_path`: str, 必填
- `[s3mount]` `cache_capacity`: int, min 1（默认值待定，历史 `<=0` 拒绝）
- `[s3mount]` `log_path`: str, 必填
- `[s3mount]` `fuse_mount_point`: str, 必填
- 注：`bucket/endpoint/accesskey/secretkey/zfspool/zvol` 等为 CLI 参数，不属 rdb config，不登记。

## 用户故事

1. 作为运维，我希望 s3tools 配置错误也以统一异常号+详情暴露，以便排障与集中日志。
2. 作为开发者，我希望 s3tools 配置键集中在注册表，避免 `atoi`+`err_msg` 漂移。

## 实现决策

- 新增/修改模块：`libs/rdb-config.c`（注册表）、`s3tools/s3file/config.{h,cpp}`、`s3tools/s3mount/config.{h,cpp}`。
- 接口：沿用 `sec_get_*` + `rdb_cfg_*_result`；`s3file_init_config`/`s3mount_init_config` 签名保持（仍返回 int）。
- 架构决策：与 T0394–T0397 完全一致，不引入新范式。

## 测试决策

- 仅测外部行为（取值/拒绝/回落），不测注册表内部。
- 先例：`libs/tests/*`、`fs-backup` `fsdeamon_config_test`。

## 验收标准

- [ ] AC-1 `[s3file]`/`[s3mount]` 全部键登记进注册表，源码无 `ini_parse`/`atoi` 直接读 rdb config。
- [ ] AC-2 缺 rdb.conf 文件（ENOENT）经调用方容忍回落注册表默认，不拒绝启动（与 fs-backup 一致：`RDB_CFG_ERR_FILE_OPEN && errno==ENOENT` 视为 ok）。
- [ ] AC-3 缺字段（cache_path/log_path/fuse_mount_point）经 `rdb_cfg_errcode_t` 拒绝，调用方直印 `detail`。
- [ ] AC-4 `parallel`/`cache_capacity` 非整数或 `<min` 经异常号拒绝。
- [ ] AC-5 `gmssl`/`verify_ssl` 非 0/1 经异常号拒绝。
- [ ] AC-6 缺省回落正确：cache_path→DEFAULT_CACHE_DIR、parallel→8、gmssl→0、verify_ssl→0。
- [ ] AC-7 单测全绿（s3file/s3mount 配置单测 + param_registry_test）。
- [ ] AC-8 全量 `xmake test` 通过。

## 范围外

- xbsa（`mini.c`）独立 XBSA 配置，不纳入。
- `bucket/endpoint/accesskey/secretkey` 等 CLI 参数不登记。

## 备注

- 决策已定：① 范围 = s3file + s3mount 都接入；② `verify_ssl` 默认保持不启用（0，与历史一致，用户裁定优先兼容，不翻安全默认），`gmssl` 默认保持 0；③ 缺 rdb.conf 文件（ENOENT）容忍回落默认（与 fs-backup 一致）。
- 部署提示：`verify_ssl` 默认不启用（0）；如需 TLS 证书校验，显式写 `verify_ssl=1`。
