---
schema: pdca.asset/v1
id: T0395-0827-rpc-config-rdb-config-integrate
phase: check
source_ids: [ev-diff, ev-build, ev-test-rpc-config, ev-test-rpc-param, ev-test-regress, ev-ac8-deploy, convergence-map]
---

## 上下文

T0394 已将 fs-backup 接入集中式 rdb config（移除自有 `do_parse_config`+`atoi` 解析器、fail-closed 严格解析）。本任务处理基类 rpc 配置加载：rpc 是共用基础库，其 `rpc-config.cpp` 自带 `do_parse_config`+`ini_parse`+`atoi` 的私有解析器，并依赖动态段名 `rpc_set_section_name(g_section_name)` 在 `[aio-speedd]`/`[aio-speed]` 间切换——这与 T0394 已统一的注册表模式重复，且动态段名在代码评审中存在歧义（F3）。目标：移除 rpc 私有解析器，tunable 注册进 rdb config 参数注册表，统一经 `sec_get_*`（env>段>默认, fail-closed）读取，并消除动态段名。

## 假设与结果

- **AC-1** rpc 配置加载不再调用任何私有 `do_parse_config`/`ini_parse`/`atoi`：`PASS` — 上述符号已从 `rpc-config.cpp` 完全移除，构建与测试均通过（ev-diff, ev-build）。
- **AC-2** 全部 rpc tunable（check_data/debug/keepalive/parallel/read_timeout/retry/fsbackup_dev_path）在 rdb config 注册表以 `PARAM_RPC_*` 注册，覆盖 `[aio-speedd]` 与回落 `[aio-speed]`：`PASS` — 新增 7 条 `PARAM_RPC_*` 表项，layer2=[aio-speedd]、layer3=[aio-speed]（ev-test-rpc-param, ev-diff）。
- **AC-3** `rpc_parse_config` 经 `sec_get_*` 正确读取默认值，缺失时回落 `[aio-speed]` 段：`PASS` — `tunables_read_from_aio_speedd`、`layer3_aio_speed_fallback` 用例覆盖（ev-test-rpc-config）。
- **AC-4** 环境变量覆盖优先于配置段：`PASS` — `env_overrides_section` 用例覆盖（ev-test-rpc-config, ev-test-rpc-param）。
- **AC-5** 布尔 tunable 仅接受全串十进制 `0`/`1`，非法（如 "true"/"false"）触发 fail-closed（`rpc_init_config`/`rpc_parse_config` 返回 -1）：`PASS` — `invalid_bool_fail_closed`、`bool_fail_closed` 用例覆盖；用 `int` 临时量承接 `sec_get_bool` 规避 `bool` 截断 `-1→1` 绕过校验（ev-test-rpc-config, ev-test-rpc-param）。
- **AC-6** 废弃动态段名 `rpc_set_section_name`，`g_section_name` 固化为 `aio-speedd`；`<tool> show` 输出据此渲染：`PASS` — `rpc_set_section_name` 改为 no-op，`rpc_get_section_name` 返回固定 `aio-speedd`，既有 show 测试无回归（ev-test-rpc-config, ev-diff）。
- **AC-7** `rpc` 库 + `aio-speedd` 可构建，且 rpc 全部单测/集成测试通过、参数注册表单测无回归：`PASS` — 构建零错误；`rpc_config_test` 8/8、`rpc_param_test` 6/6、`rdb_config_test` 15/15、`param_registry_test` 9/9 全绿，无回归（ev-build, ev-test-regress, ev-test-rpc-config, ev-test-rpc-param）。
- **AC-8** 生产部署侧确认：生产 `rdb.conf` 须将布尔写成 `0`/`1`、数值为严格整数、嵌入方未推送的 `fsbackup_dev_path` 经 `[aio-speed]` 回落（或默认 `/dev/fsbackup`）：`PARTIAL/延迟` — 属发布前部署侧确认项，已登记延迟证据 `ev-ac8-deploy`，不阻塞本轮 confirmed（ev-ac8-deploy）。

## 分析

- 每个 tunable 注册**单条** `PARAM_RPC_*`（layer2=[aio-speedd] 优先、layer3=[aio-speed] 回落），既覆盖两段又消除动态段名；同时规避了 F4 误报（"动态段名解决不了 fs-backup 缺失"实为 `rpc_set_section_name` 仅设 `g_section_name` 用于 show，不影响读取路径）。
- **零回归保障**：fs-backup 仅通过 `set_rpc_*` 推送 check_data/keepalive/retry（及 T-mtls 任务的 read_timeout/parallel），**从不推送** `fsbackup_dev_path`；旧实现该字段来自 `[aio-speed]`，新实现经 layer3=[aio-speed] 回落，取值完全一致。`rpc_param_test`/`rdb_config_test` 回归用例确认无行为变化。
- **fail-closed 对齐**：与 T0394 及既有 `audit_enable`/`auth_enable` 约定一致，`sec_parse_strict_bool` 仅接受 `0`/`1`，非 0/1 全串拒绝（含 "true"）并 fail-closed。
- **libs 不反向依赖 rpc**：`DEFAULT_DEV_PATH` 定义在 `rpc-config.h`，`libs` 不可引用，故在 `rdb-config.h` 新增本地宏 `RDB_DEFAULT_DEV_PATH`（同值 `/dev/fsbackup`），STR 缺失/非法回落该默认，不 fail-closed。
- **store 重载语义**：`rpc_parse_config` 仅当 `config_file!=NULL` 时重载全局 store（配置重载路径），`rpc_init_config` 透传原始 `config_file`（NULL 时不重载，读取已加载 store），避免测试临时 ini 被默认路径冲掉；解析失败时 `g_rpc_config` 不切换（fail-safe）。

## 适用边界

- 嵌入方（fs-backup 等）若依赖旧 `atoi` 宽松语义（如 `"keepalive = 30s"`），须改用严格整数，否则回落默认。
- 生产 `rdb.conf` 的布尔字段须为 `0`/`1`，否则 aio-speedd/aio-speed 将以 fail-closed 拒绝启动（与既有安全开关一致）。
- `sbt.conf` 不属本 rdb config 接入范围。

## 下一轮建议

- AC-8 为发布前部署侧确认项：依 `ev-ac8-deploy` 复核生产 `rdb.conf`，发现旧写法先评估告警+回落默认是否符合预期。
- 后续若有更多工具段需回落 `[aio-speed]`，可复用本任务确立的 layer3 回落模式（已沉淀知识：见 Act 阶段知识处置）。
