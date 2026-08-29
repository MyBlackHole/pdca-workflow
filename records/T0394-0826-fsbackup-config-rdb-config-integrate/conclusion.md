---
schema: pdca.asset/v1
id: T0394-0826-fsbackup-config-rdb-config-integrate
phase: check
source_ids: [ev-diff, ev-build, ev-test-fsdaemon, ev-test-param, ev-test-regress, ev-ac8-deploy, convergence-map]
---

## 上下文
fs-backup（fsdeamon / fsclient）原先使用自有 `do_parse_config` + `ini_parse` + `atoi` 解析 `[fsdaemon]`/`[fsclient]` 段，与集中式 rdb config 的严格解析语义不一致。本次按"统一管理参数"要求，将其配置项注册进 rdb config 参数注册表（`PARAM_*`），读取改为 `sec_get_*`（env > 工具段 > 默认，fail-closed），并保留 `set_rpc_*` 传播副作用。

## 假设与结果
- 假设：集中式 rdb config 的 `sec_get_*` 可正确承接 fs-backup 既有 `[fsdaemon]`/`[fsclient]` 配置（layer2 指向这两段）。
- 结果：在 `g_param_table` 新增 9 个 `PARAM_*` 项（fsdaemon: check_data/debug/keepalive/retry；fsclient: check_data/retry/keepalive/read_timeout/parallel），`fsdeamon_parse_config`/`fsclient_parse_config` 改用 `sec_get_bool`/`sec_get_int` 读取，reload 经 `parse_config(config_path)` 刷新 store。构建与单测全部通过，既有 rdb 注册表测试无回归。

## 分析
- **AC-1** ✅ fsdeamon 删除 `do_parse_config`/`ini_parse`，改经注册表 `sec_get_*` 读取 `[fsdaemon]` 四项（ev-diff, ev-test-fsdaemon）
- **AC-2** ✅ fsclient 删除自有解析器，改经 `sec_get_*` 读取 `[fsclient]` 五项含 read_timeout/parallel（ev-diff, ev-test-param）
- **AC-3** ✅ 构造合法 `[fsdaemon]`/`[fsclient]` 值，init 后 `g_pConfig` 各字段与配置一致（ev-test-fsdaemon, ev-test-param）
- **AC-4** ✅ 脏值 `check_data=2` 经 `sec_get_bool` 返回 -1 触发 fail-closed 拒绝启动；INT 脏值回退默认并 stderr 告警（ev-test-fsdaemon, ev-test-param）
- **AC-5** ✅ `xmake build fs-cli fsdeamon` 及新增 `fsdeamon_config_test`/`rdb_param_test` 全部 build ok 且用例 PASS（ev-build, ev-test-fsdaemon, ev-test-param）
- **AC-6** ✅ rdbcomm/libobk 代码未改动；既有 `rdb_config_test`(15 passed)/`param_registry_test`(9 passed) 无回归（ev-test-regress, ev-build）
- **AC-7** ✅ 保留 `set_rpc_check_data`/`set_rpc_keepalive_interval`/`set_rpc_retry`（及 fsclient 的 `set_rpc_read_timeout`/`set_rpc_parallel`）；`fsdeamon_config_test` 以桩记录 `set_rpc_*` 调用值，验证传播与配置一致（ev-test-fsdaemon）
- **AC-8** ❌ 部署侧确认项（生产 rdb.conf 的 `[fsdaemon]`/`[fsclient]` 数值均为严格整数）未在生产环境验证，非代码缺陷；已登记延迟证据 ev-ac8-deploy，列为发布前待办，不阻塞 confirmed 结论

## 适用边界
- 仅覆盖 fs-backup 配置读取路径；sbt.conf（dmsbtex）不在范围（按用户指令）。
- fsclient 未做独立单测（其 `config.h` 引入 `fs_service_proto.h` 重依赖），正确性由与 fsdeamon 同构的代码、`fs-cli` 构建、`rdb_param_test` 覆盖其 5 个新 PARAM 解析链共同保证。
- BOOL 字段（`check_data`/`debug`）采用 `int` 临时量预校验，避免 `bool` 截断 `-1`→`1` 绕过 fail-closed；INT 字段沿用宽松语义（非法值回退默认），与历史 `atoi` 一致。

## 下一轮建议
- 发布前完成 AC-8 部署侧确认：核查生产 rdb.conf 的 `[fsdaemon]`/`[fsclient]` 数值是否含单位后缀等非严格整数；如发现，按 PRD RISK A 评估告警+回退默认是否符合预期。
- 后续可将 s3tools / xbsa 配置接入纳入统一参数管理议题。
