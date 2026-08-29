# T0396：rdb config 注册表支持 min/max/maxlen 与 invalid_policy，并下沉工具范围校验

## 背景

T0394/T0395 已将 fs-backup 与 rpc 的配置加载统一接入集中式 rdb config 参数注册表
（`libs/rdb-config.c` 的 `g_param_table` + `sec_get_*`）。但当前注册表只做**类型解析**：
- `sec_walk_int`：严格整型解析（`parse_strict_int`），非整数串→-1（fail-closed），但**不校验数值范围**（如 `keepalive = -5` 会原样返回 -5）。
- `sec_walk_str`：返回原始串，长度仅靠调用方 `snprintf` 缓冲截断兜底，无显式长度策略。
- 数值范围校验（retry>0 / keepalive>=0 / parallel>=1 等）仍**散落在各工具侧** `rpc_check_config` / `fsdeamon_check_config` / `fsclient_check_config`，与解析逻辑重复，且每工具自行维护易漂移。

目标：把"通用、机械的边界约束"（INT 的 [min,max]、STR 的 maxlen）**声明式下沉到注册表**，由 `sec_get_*` 统一执行；工具侧仅保留注册表表达不了的跨参数语义不变量。

## 目标

- 在 `config_param_desc_t` 增加声明式边界字段：`long min; long max;`（INT）、`size_t maxlen;`（STR）、`cfg_invalid_policy_t invalid_policy`（默认 `CFG_INVALID_FAIL_CLOSED`）。
- `sec_get_int` / `sec_get_str` 按 policy 执行边界：越界→`FAIL_CLOSED` 返回 -1/NULL，或 `FALLBACK_DEFAULT` 回落默认（带 stderr 告警）。
- 将现有工具侧 INT 范围检查编码进注册表（每参数 `min`），并移除工具侧冗余范围检查；行为保持 fail-closed 不变。
- STR 参数（fsbackup_dev_path、cert_dir）设 `maxlen` + `FALLBACK_DEFAULT`，移除调用方 `snprintf` 截断，改由注册表回落默认。

## 范围

- 受影响文件：`libs/rdb-config.h`（ParamDesc + 枚举/宏 + 新 API）、`libs/rdb-config.c`（`sec_walk_int`/`sec_walk_str` + `g_param_table` 各 INT/STR 参数补 `min`/`maxlen`/`invalid_policy`）、
  `rpc/rpc-config.cpp`（`rpc_check_config` 去冗余）、`fs-backup/fsdeamon/config.cpp`、`fs-backup/fsclient/config.cpp`（去冗余范围检查）。
- 测试：`libs/tests/` 注册表单测新增 [min,max]、maxlen 的 fail_closed 与 fallback 两路径；现有 `rpc_config_test`/`rpc_param_test`/`rdb_config_test`/fs-backup 单测无回归（含越界用例）。

## 非目标

- 跨参数语义不变量（如"dev_path 与 retry 的联动"）仍留在工具侧，不进注册表。
- 新增参数或改变各参数既有默认值。
- 改变 BOOL 语义（BOOL 已严格 0/1 fail-closed，本次不动）。
- 全局 `config_get_*` 底层 API 的语义变更（仅注册表层封装增强）。

## 设计

### 1. ParamDesc 扩展
```c
typedef enum { CFG_INVALID_FALLBACK_DEFAULT = 0, CFG_INVALID_FAIL_CLOSED = 1 } cfg_invalid_policy_t;
typedef struct {
  const char *env_name;
  const char *layer2_section; const char *layer2_key;
  const char *layer3_section; const char *layer3_key;
  config_param_type_t type;
  const char *def;
  const char *desc;
  long min; long max;          /* INT：合法闭区间 [min,max]；默认 LONG_MIN/LONG_MAX 表示不限制 */
  size_t maxlen;               /* STR：最大长度（不含 NUL）；0 表示不限制 */
  cfg_invalid_policy_t invalid_policy; /* 越界策略；默认 FAIL_CLOSED */
} config_param_desc_t;
```
为兼容既有表项（静态初始化），新增字段置于末尾并提供合理零值默认（`min=LONG_MIN, max=LONG_MAX, maxlen=0, invalid_policy=FAIL_CLOSED`）。

### 2. sec_walk_int 增强
解析得到严格整数 `iv` 后（`sec_parse_strict_int` 已保证为整数）：
- 若 `iv < min || iv > max`：按 `invalid_policy`——`FAIL_CLOSED` 返回 -1；`FALLBACK_DEFAULT` 解析 `def` 为整数返回（def 非法则 -1）。
- 现有 INT 参数均设 `invalid_policy = FAIL_CLOSED` 以保持与工具现状一致的 fail-closed。

### 3. sec_walk_str 增强
取得候选串 `val` 后：
- 若候选串**来自某一层且非空**（key 存在）：`maxlen > 0 && strlen(val) > maxlen` → 按 `invalid_policy` 处理。`dev_path`/`cert_dir` 设 `FAIL_CLOSED`：**超长拒绝报错**（返回 NULL，调用方 fail-closed 拒绝启动）。
- key **缺失/全空** → 仍走 `def` 回落（既有行为，不 fail-closed）——与 T0395 裁定一致（dev_path 缺失回落默认）。
- 调用方（如 rpc 的 `dev_path` 拷贝）改为直接 `sec_get_str` 结果；移除手写 `snprintf` 截断兜底（超长现已由注册表在解析阶段拒绝）。

### 4. 参数边界映射（编码现有工具检查）
| 参数 | min | max | 依据（原工具检查） |
|------|-----|-----|------|
| PARAM_RPC_RETRY | 1 | — | rpc_check_config: retry>0 |
| PARAM_RPC_KEEPALIVE | 0 | — | rpc/fs-backup: keepalive>=0 |
| PARAM_RPC_PARALLEL | 1 | — | rpc/fsclient: parallel>=1 |
| PARAM_RPC_READ_TIMEOUT | 1 | — | rpc 现状未校验范围，按裁定补 min>=1（fail-closed） |
| PARAM_FSDEAMON_RETRY | 0 | — | fsdeamon_check_config: retry>=0 |
| PARAM_FSCLIENT_RETRY | 1 | — | fsclient_check_config: retry>0 |
| PARAM_FSDEAMON_KEEPALIVE | 0 | — | fsdeamon_check_config: keepalive>=0 |
| PARAM_FSCLIENT_KEEPALIVE | 0 | — | fsclient_check_config: keepalive>=0 |
| PARAM_FSCLIENT_PARALLEL | 1 | — | fsclient_check_config: parallel>0 |
| PARAM_FSCLIENT_READ_TIMEOUT | 1 | — | fsclient 现状未校验范围，按裁定补 min>=1（fail-closed） |
| PARAM_RPC_DEV_PATH | — | 4095 | fsbackup_dev_path 路径上限；超长 FAIL_CLOSED（拒绝报错），缺失仍回落默认 |
| PARAM_CERT_DIR | — | 4095 | 证书目录路径上限；超长 FAIL_CLOSED（拒绝报错），缺失仍回落默认 |
> 注：`read_timeout` 当前工具未做范围校验，本次维持"仅严格整型"不新增 min，避免行为变更（如需正向下限，后续单列）。

### 5. 工具侧去冗余
- `rpc_parse_config`：`p_config->keepalive = sec_get_int(...)` 等改判 `int v = sec_get_int(id); if (v < 0) { snprintf(err,"invalid %s (expect >=%ld)", key, min); return -1; }`。
- 移除 `rpc_check_config` 中 retry/keepalive/parallel/check_data/debug 的冗余范围与 BOOL 检查（BOOL 已由 `sec_get_bool` 在 parse 阶段 fail-closed 预校验，`rpc_parse_config` 已有 int 临时量承接）。
- 同步移除 `fsdeamon_check_config` / `fsclient_check_config` 中 retry/keepalive/parallel 的冗余范围检查；保留函数签名（调用点不变）或按需精简。

## 验收标准

- [ ] AC-1 `config_param_desc_t` 支持 `min`/`max`(INT)、`maxlen`(STR)、`invalid_policy`，零值默认保持现有语义（FAIL_CLOSED、不限制）。
- [ ] AC-2 `sec_get_int` 越界按 policy 返回 -1（FAIL_CLOSED）或回落默认整数（FALLBACK_DEFAULT）；`sec_get_str` 超长按 policy 返回 NULL 或回落默认；`parse_config` 重载不受影响。
- [ ] AC-3 现有 rpc/fs-backup 的 INT 范围（retry/keepalive/parallel 等）以 `min` 编码进注册表，工具侧冗余范围检查已移除，fail-closed 行为不变（越界仍拒绝启动）。
- [ ] AC-4 `fsbackup_dev_path`/`cert_dir` 设 `maxlen`+`FAIL_CLOSED`，调用方移除 `snprintf` 截断兜底；超长**拒绝报错**（返回 NULL，fail-closed），key 缺失仍回落默认，且经测试确认。
- [ ] AC-5 注册表单测覆盖 [min,max]、maxlen 的 fail_closed 与 fallback 两路径；`rpc_config_test`/`rpc_param_test`/`rdb_config_test`/fs-backup 单测无回归（含越界输入）。
- [ ] AC-6 `libs`(含 rdb-config/rpc 依赖) 与 fs-backup 构建零错误；全仓相关单测通过。
- [ ] AC-7 发布前部署侧确认：生产 rdb.conf 的 INT 参数须在 [min,max]（越界 fail-closed，与既有工具 check 一致），延迟登记部署证据，不阻塞 confirmed。
