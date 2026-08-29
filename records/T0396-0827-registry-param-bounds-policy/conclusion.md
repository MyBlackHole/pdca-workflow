---
schema: pdca.asset/v1
id: T0396-0827-registry-param-bounds-policy
phase: check
source_ids: [ev-diff, ev-build, ev-test-all, ev-ac7-deploy, convergence-map]
---

## 上下文

T0394/T0395 已将 fs-backup 与 rpc 的配置加载统一接入集中式 rdb config 注册表，但注册表只做**类型解析**（INT 严格整型、STR 原样、BOOL 严格 0/1），**数值范围与字符串长度仍散落在各工具侧** `*check_config`。本任务把"通用、机械的边界约束"声明式下沉到注册表 ParamsDesc（INT 的 [min,max]、STR 的 maxlen、invalid_policy），由 `sec_get_*` 统一执行；工具侧冗余范围/BOOL 检查移除，行为保持 fail-closed 不变。

## 假设与结果

- **AC-1** `config_param_desc_t` 新增 `restrict_range`/`min`/`max`(INT)、`maxlen`(STR)、`invalid_policy`：零值默认安全（restrict_range=0 不限制、maxlen=0 不限制、invalid_policy=0=FAIL_CLOSED），既有未显式声明的参数行为不变：`PASS`（ev-diff）。
- **AC-2** `sec_get_int` 越界按 policy 返回 -1（FAIL_CLOSED）或回落默认整数（FALLBACK_DEFAULT）；`sec_get_str` 超长按 policy 返回 NULL 或回落默认；新增 `sec_test_int_bounds`/`sec_test_str_bounds` 测试接缝：`PASS`（ev-diff, ev-test-all）。
- **AC-3** 现有 rpc/fs-backup 的 INT 范围（retry/keepalive/parallel/read_timeout 等）以 `min` 编码进注册表，工具侧 `*check_config` 冗余范围与 BOOL 检查已移除（改为 parse 阶段检测 `sec_get_int<0` 失败并产出可读错误），fail-closed 行为不变：`PASS`（ev-diff, ev-test-all：rpc `out_of_range_tunable_fail_closed`、fs-backup `fsdeamon_config_test` 全绿）。
- **AC-4** `fsbackup_dev_path`/`cert_dir` 设 `maxlen=4095` + `FAIL_CLOSED`，调用方（rpc）移除手写 `snprintf` 截断兜底；超长拒绝启动（NULL）、key 缺失仍回落默认：`PASS`（ev-diff, ev-test-all：`sec_get_str_overlength_fail_closed_real`）。
- **AC-5** 注册表单测覆盖 [min,max]、maxlen 的 fail_closed 与 fallback 两路径（`sec_test_int_bounds_both_policies`/`sec_test_str_bounds_both_policies`），并用真实参数验证越界 fail-closed 与缺失回落；`rdb_config_test` 19/19、`rpc_config_test` 9/9、`rpc_param_test` 6/6、`param_registry_test` 9/9、`fsdeamon_config_test` 全绿，无回归：`PASS`（ev-test-all）。
- **AC-6** `libs`(rdb-config + 依赖)/`rpc`(aio-speedd)/`fs-backup` 构建零错误；全仓相关单测通过：`PASS`（ev-build, ev-test-all）。
- **AC-7** 发布前部署侧确认：生产 rdb.conf 的 INT 参数须在 [min,max]（越界 fail-closed，与既有工具 check 一致），dev_path/cert_dir 超长拒绝；已登记延迟证据 `ev-ac7-deploy`，不阻塞 confirmed：`PARTIAL/延迟`。

## 分析

- **下沉而非新增约束**：仅把工具已存在的范围（retry>0/keepalive>=0/parallel>=1 等）编码为 `min`，未对"未做范围校验"的参数（如 read_timeout 经裁定补 min>=1）引入无依据上限；`restrict_range=0` 的参数（mTLS/算法等）行为完全不变。
- **零值默认安全**：新字段置于结构体末尾，静态表项未显式赋值即零初始化 → 不限制/FAIL_CLOSED，避免"默认 [0,0] 误伤所有 INT 参数"的坑；仅对确需约束的 10 个 INT + 2 个 STR 显式声明。
- **fail-closed 一致性**：越界语义与 T0394/T0395 既定布尔严格 0/1 一致；`sec_walk_int` 改为先 `config_get_string` 取原始串再 `parse_strict_int`，非整数层直接 fail-closed（不再静默回落下一层），与 T3981 严格解析哲学统一。
- **STR 超长拒绝报错**（按裁定）：区别于"缺失回落默认"——`sec_walk_str` 仅当 key 存在且超长时返回 NULL（fail-closed），缺失/空仍走 `def` 回落，与 T0395 裁定无冲突。

## 适用边界

- 跨参数语义不变量（如"dev_path 与 retry 联动"）仍保留在工具侧 `*check_config`（当前无此类约束，函数为空壳占位）。
- 生产部署须确认 INT 取值在 [min,max]、dev_path/cert_dir 不超长，否则 fail-closed 拒绝启动。

## 下一轮建议

- 如需为某参数"超界回落默认"而非拒绝，将其 `invalid_policy` 改为 `CFG_INVALID_FALLBACK_DEFAULT` 即可，无需改调用方（已通过 `sec_test_int_bounds`/`sec_test_str_bounds` 单测覆盖）。
- 后续新增工具接入注册表时，直接在 ParamDesc 声明 min/max，无需再写工具侧范围检查。
