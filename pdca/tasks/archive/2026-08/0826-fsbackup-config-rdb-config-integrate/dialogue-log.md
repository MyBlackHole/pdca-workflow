# Dialogue Log — T0394

## Plan → Do
- 要点：fs-backup（fsdeamon/fsclient）移除自有 `do_parse_config`+`ini_parse`+`atoi`，统一接入集中式 rdb config；用户指令范围收敛为仅 rdb config（sbt.conf 不在范围）。
- 被否决备选：最初方案用 `config_get_int(store, section, key)` 原始读取；用户指示"统一管理参数"后改为注册表 `PARAM_*`+`sec_get_*`，否决原始读取方案。
- 用户关键反应："还有统一管理参数"（要求纳入参数注册表）；"风格应该于 rdb config 一致"（代码习语对齐）。
- 未解决疑点：无（self-review 已覆盖 set_rpc_* 传播、reload、测试前置）。

## Do → Check
- 要点：在 `libs/rdb-config.c` 注册 9 个 `PARAM_*`（fsdaemon 4 + fsclient 5），fs-backup 改经 `sec_get_bool`/`sec_get_int` 读取；BOOL 字段用 int 临时量预校验防 bool 截断绕过 fail-closed；fsclient 本地 `parse_config` 改名 `fsclient_parse_config`；新增 `fsdeamon_config_test`/`rdb_param_test` 单测（桩记录 set_rpc_*）。
- 被否决备选：让 fsclient 单独链接单测——因 `config.h` 引入 `fs_service_proto.h` 重依赖而否决，改由同构代码 + fs-cli 构建 + 注册表单测共同覆盖。
- 用户关键反应：verdict 选择 "confirmed（推荐）"。
- 未解决疑点：AC-8 生产配置严格整数确认，列为发布前部署侧待办（已登记延迟证据 ev-ac8-deploy）。

## Check → Act
- 要点：verdict=confirmed，沉淀可复用知识 `knowledge/rdb-config/wire-tool-config-to-registry.md`（BOOL 截断陷阱 + 接入模式）；`meta.disposition=projected`；journal 当日摘要。
- 用户关键反应：收尾选择 "仅归档不提交"（PDCA 仓与代码仓均不 git commit）。

## Act → Archive
- 归档方式：仅 advance-phase --to archive + 移动任务目录，不执行 git commit（用户显式选择）。
