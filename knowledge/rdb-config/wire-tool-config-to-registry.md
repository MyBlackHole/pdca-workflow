# 将工具配置接入 rdb config 参数注册表的复用要点

## 背景
fs-backup（fsdeamon/fsclient）原用自有 `do_parse_config`+`ini_parse`+`atoi` 解析
`[fsdaemon]`/`[fsclient]` 段。统一接入集中式 rdb config 时，采用"参数注册表"模式：
在 `libs/rdb-config.c` 的 `g_param_table` 新增 `PARAM_*` 项，工具侧改经 `sec_get_*`
（env > 工具段 > 默认，fail-closed）读取，并保留既有"配置传播副作用"（如 `set_rpc_*`）。

## 关键陷阱（可复用）
**BOOL 字段截断绕过 fail-closed**：`sec_get_bool` 对非法值（非 "0"/"1"）返回 `-1`
（fail-closed 语义）。若目标字段是 C/C++ `bool`（如 `Config.check_data`），直接
`field = sec_get_bool(...)` 会把 `-1` 截断为 `1`，使非法值被静默视作"真"，
**绕过 fail-closed**。

正确写法：先用 `int` 临时量承接，预校验 `v < 0` 即拒绝启动，再赋值：
```c
int v = sec_get_bool(PARAM_X_CHECK_DATA);
if (v < 0) { snprintf(err, len, "invalid [...]check_data"); return -1; }
tmp.check_data = (bool)v;
```
INT 字段（`sec_get_int`）为宽松语义：非法值回退默认并 stderr 告警，与历史 `atoi` 一致，
无截断问题，但脏值不再"部分解析"，属有意强化。

## 接入步骤（通用）
1. 在 `rdb-config.h` 枚举 `config_param_id_t` 与 `*_ENV` 宏新增参数；在 `g_param_table`
   登记（layer2 指向工具段，类型 BOOL/INT，默认与历史一致；非全局安全策略者 layer3 置 NULL）。
2. 工具侧删除自有 `atoi` 解析器，改经 `sec_get_bool`/`sec_get_int`；BOOL 按上法预校验。
3. 保留读取后的传播副作用（如 `set_rpc_*`）。
4. reload：经 `parse_config(config_path)` 刷新全局 `_kv_store` 后重读；rpc 已在 init 时
   把 `sec_*` 缓存进自有 struct，无副作用。
5. 本地与全局 `parse_config` 同名冲突时，将工具的 `static parse_config` 改名
   （如 `fsclient_parse_config`）。

## 测试接缝
- 链接 `rdb-config` + `set_rpc_*` 桩（不链真实 rpc），构造临时 rdb.conf 调用
  `xxx_init_config` 断言取值与桩记录的传播调用；覆盖非法 BOOL 拒绝启动与缺省回退。
- 仅链 `rdb-config` 的注册表单测可验证全部 `PARAM_*` 的 env>工具段>默认 解析链。
- 重依赖头文件（如 `fs_service_proto.h`）会阻碍某工具独立链接单测时，由同构代码 +
  构建 + 注册表单测共同覆盖，不强行隔离。


## 覆盖两段 / 动态段名废弃（T0395 补充）

- **单条 PARAM 覆盖多段**：一个工具可能同时被多段配置（如 rpc 既读
  `[aio-speedd]` 服务端权威段，又读 `[aio-speed]` 嵌入方段）。不要为每个段各注册
  一条 `PARAM`（14→7 收敛）：注册**单条** `PARAM_RPC_*`，`layer2` 指向权威段
  （aio-speedd）、`layer3` 指向回落段（aio-speed）；解析序 env > layer2 > layer3 > def。
- **动态段名应废弃为 no-op**：运行时切换 `g_section_name` 在 `[aio-speedd]`/`[aio-speed]`
  间（如旧 `rpc_set_section_name`）应改为 no-op。注册表按 (layer2, layer3) 直接定位多段，
  无需运行时切段；`<tool> show` 等需段名处固定读 `AIO_SPEEDD_TOOL_SECTION`。这消除了
  "动态段名能否覆盖未推送键"的歧义（F3/F4 类误报根源）。
- **嵌入方未推送键零回归**：嵌入方（如 fs-backup）经 `set_rpc_*` 只推送部分键、不推送
  的键（如 `fsbackup_dev_path`）经 layer3 回落原段，取值与旧实现一致，须用 layer3 用例
  在单测中确认零回归。

## ini key / env 单点定义（T0395 补充）

- 注册表 `ParamDesc` 的 `.key`（ini key）与 `_ENV`（env 名）都应走宏：
  `RPC_TOOL_*_KEY` 与 `RPC_TOOL_*_ENV`（定义在 `rdb-config.h`），**不要硬编码字面量**。
  fs-backup 与 rpc 共用同一组 key，宏化避免拼写漂移与双份字面量；检查项：grep
  确认 `g_param_table` 中无裸 `"check_data"` 等字符串。

## 声明式边界下沉（T0396 补充）

- **通用边界写在注册表，不写在工具**：INT 的 `[min,max]`、STR 的 `maxlen`、越界策略
  `invalid_policy` 是"通用、机械"的约束，应声明式写进 `config_param_desc_t`，由 `sec_get_*`
  统一执行；**不要**在工具侧 `*check_config` 重复写范围/长度检查（重复实现易漂移且难统一）。
- **字段零值默认安全**：`restrict_range=0`=不限制、`maxlen=0`=不限制、
  `invalid_policy=0`=FAIL_CLOSED。仅对确需约束的参数显式声明 `min/max/maxlen`；
  未声明的参数保持宽松（历史 `atoi`/`snprintf` 行为），避免"默认 [0,0] 误伤所有 INT"。
- **测试接缝**：`sec_test_int_bounds(p,val)`/`sec_test_str_bounds(p,val)` 返回
  `1`=合法、`-1`=FAIL_CLOSED、`0`=FALLBACK_DEFAULT，供注册表单测覆盖两策略三态。
- **解析序改动**：`sec_walk_int` 先 `config_get_string` 取原始串再 `parse_strict_int`，
  越界按 policy 返回 `-1` 或回落默认整数（不再静默滚下一层）；`sec_walk_str` 超长返回
  `NULL`（FAIL_CLOSED）或回落，`key` 缺失仍走 `def`（与"缺失回落"裁定一致）。
  - **工具侧收敛**：范围/长度校验全部下沉到注册表 `ParamDesc`，**工具侧不保留空壳
    `*check_config`**（纯占位、调用恒 0 属死代码，应删除，与 s3tools 一致）。跨参数语义
    不变量若确有必要再新增具体校验函数，不要预置空壳占位。新工具接入直接在 `ParamDesc` 声明边界。
- **STR 超长裁定**：按审查结论"拒绝报错"，区别于"缺失回落默认"——调用方（rpc）移除手写
  `snprintf` 截断兜底，由注册表在 `maxlen` 越界时 FAIL_CLOSED 拒绝启动。

## 错误号+异常详情上抛（T0397 补充）

- **错误归属调用方，库不自行打印**：`sec_get_*`/`parse_config`/`init_config` 失败经
  `rdb_cfg_*_result`（`ok`/`value`/`code`/`detail[160]`）出参指针回传，函数返回 `int`（=ok）；
  失败 `code` 取自 `rdb_cfg_errcode_t`（独立枚举，非 errno，数值稳定、可运维查询），`detail`
  精确含取值来源（env/[段]键）、取值、原因。`rdb-config` 内部不再有 `fprintf`/stderr 打印，
  错误完全由调用方据 `detail` 记录——库不替调用方决定如何输出。
- **API 形态裁定**：出参指针 + `int` 返回（非按值返回、非线程局部、非全局诊断回调注册）。
  调用方 `if (sec_get_int(id,&r))` 判成功；失败时直印 `r.detail`，禁止自造 `invalid %s value`
  类模糊文案。
- **截断不静默不打印**：`CONFIG_KV_MAX` 超限不再内部打印，改经 `parse_config` 返回
  `code=RDB_CFG_ERR_TRUNCATED` 且 `detail` 描述截断条数/文件，由调用方决定告警。
- **fail-closed 不变**：非法 BOOL 维持开启、越界/超长拒绝启动、缺失回落默认；调用方迁移范式
  BOOL 仅 `value==0` 才关闭（`!r.ok` 维持开启）、安全 STR `!r.ok` 必须拒绝启动（不得把
  `r.value==NULL` 当默认）、INT `!r.ok` 拒绝。`sec_walk_*` 开头 `memset` 初始化 result，
  失败路径 `value` 确定性为 0/NULL，防御调用方误读。
- **INT 非整数维持 fail-closed 拒绝**（不回退默认）：`keepalive=30s` 类非纯十进制整数
  → `code=RDB_CFG_ERR_INT_INVALID`；注册表描述"非法值回退默认"应写作"非整数 fail-closed 拒绝"。
- **跨模块复用**：rpc/fs-backup/rdbcomm/libs/dmsbtex/libobk 已全部按此范式迁移；新增工具接入
   注册表时直接消费 `r.code`+`r.detail` 即可获得统一错误归因，无需各自实现错误码/打印。

## s3tools 接入（T0398 补充）

- **全工具统一完成**：s3file/s3mount 已接入注册表（新增 `PARAM_S3FILE_*` /
  `PARAM_S3MOUNT_*` 共 8 条）。至此读取 rdb config 的工具已全覆盖
  rpc/fs-backup/rdbcomm/libs/dmsbtex/libobk/s3tools；xbsa 走独立 XBSA 配置，**不在范围**。
- **ENOENT 容忍不得绕过必填校验（关键陷阱）**：`init_config` 在 `parse_config`
  返回 `ENOENT` 时若直接 `return 0`，会跳过后续 `sec_get_*` 必填校验，使"文件允许不存"
  的宽容把必填字段也放过（s3mount `cache_capacity` 必填无默认 → 静默为 0，历史要求必填启动
  会失败）。正确写法：
  ```c
  rdb_cfg_parse_result pr;
  parse_config(config_path, &pr);
  /* ENOENT 只容忍"解析错误"，不提前返回，继续走下方 sec_get_* */
  if (!pr.ok && !(pr.code == RDB_CFG_ERR_FILE_OPEN && errno == ENOENT)) {
      snprintf(err, len, "parse rdb config failed: %s", pr.detail);
      return -1;
  }
  /* 必填字段（def=NULL）在 store 为空时仍以 INT_MISSING fail-closed 拒绝 */
  ```
  效果：s3file 无必填→缺文件仍 `rc=0`；s3mount 有必填→缺文件 `rc=-1`（与历史必填语义一致）。
- **STR 取值只需判 `!r.ok`**：`sec_walk_str` 内部 `v && v[0]` 已把空串当无值回落默认/MISSING，
  `ok=1` 时 `value` 必非空，调用方无需额外 `!r.value || r.value[0]=='\0'` 冗余判断。
- **默认值单一来源**：工具的 `config.h` 中 `DEFAULT_CACHE_DIR` / `DEFAULT_LOG_DIR` /
  `DEFAULT_MOUNT_POINT` 等死宏应**删除**，统一引用 `rdb-config.h` 的 `RDB_DEFAULT_S3_*`；
  避免两处默认值漂移（本次已清理 s3tools 的重复宏）。
- **verify_ssl 默认保持不启用（0）**：与历史一致，未翻为"安全默认开启"；属有意保持。
