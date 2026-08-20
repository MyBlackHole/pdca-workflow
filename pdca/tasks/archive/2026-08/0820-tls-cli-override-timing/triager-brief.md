# Triage Brief — tls-cli-override-timing

- **category**: enhancement
- **scenario_type**: development
- **summary**: 修正 `sec_tool_tls_set_cli_overrides` 的调用时序与默认值加载，使程序启动立即生效 env/config 默认值，CLI 参数解析后存在则覆盖。
- **current behavior**: 三个入口（rdbcomm-main/rdbcommd-main/rpc-client）在 `args_process` 之后一次性调用 `sec_tool_tls_set_cli_overrides`（全量替换三值）。若模块早期代码（daemon/supervise 流程或库初始化）在参数解析前读取 TLS 配置，会读到未覆盖的 env/config 值；`set_cli_overrides` 内部 `sec_cache_reset()` 重置缓存依赖"调用顺序恰好正确"，时序脆弱。
- **desired behavior**: 启动即加载 env/config 默认值（首个 TLS 配置读取前即生效）；CLI 参数解析后若存在 `--mtls-enable`/`--tls-algorithm` 则覆盖默认值。覆盖语义保持全量替换（用户已确认）。
- **key interfaces**: `sec_tool_tls_enabled`、`sec_tool_tls_algorithm`、`sec_tool_tls_set_cli_overrides`、`sec_cache_reset`；rdbcomm/rdbcommd/rpc-client 三个 main 的启动时序。
- **acceptance criteria**: 启动早期（参数解析前）读取 TLS 配置得到 env/config 默认值；参数解析后 CLI 覆盖生效；缓存状态与覆盖语义一致。
- **out of scope**: 不改变 TLS 证书加载、握手协议、profile 模型；不改变 CLI 参数名与取值规则；不改变 `sec_*` 其它配置接口。
- **information gaps**: 需盘点三个 main 启动到 args_process 之间是否有 TLS 配置读取路径（daemon/supervise/库初始化）。
- **dedup results**: 与 T0322（0819-tool-mtls-cli-args-v2）直接相关，本次为 T0322 引入的 CLI 覆盖机制之后续修正。
- **recommended next steps**: 盘点三个入口启动时序；设计"启动加载默认值 + 解析后覆盖"的调用模式；写 prd 后进入 Do。