## Check 阶段摘要（2026-08-27）

- 结论：rpc 配置加载统一接入集中式 rdb config，移除私有 do_parse_config/ini_parse/atoi 解析器，tunable 注册为单条 PARAM_RPC_*（layer2=[aio-speedd] 优先、回落 layer3=[aio-speed]），fail-closed 严格解析；rpc_set_section_name 废弃为 no-op，段名固化 aio-speedd。
- 用户审查发现：ini key 字面量未用宏 → 已新增 RPC_TOOL_*_KEY 宏并全量替换（fs-backup+rpc 两段），复验通过。
- 验证：validate-convergence valid:true；aio-speedd 构建零错误；rpc_config_test 8/8、rpc_param_test 6/6、rdb_config_test 15/15、param_registry_test 9/9 全绿，无回归。
- Verdict：confirmed（V-T0395-20260827-001）；AC-8 为发布前部署侧延迟确认（ev-ac8-deploy）。
