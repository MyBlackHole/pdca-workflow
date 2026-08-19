# Triage Brief — 0819-tool-mtls-cli-args-final

- **category**: enhancement
- **scenario_type**: development
- **summary**: 四个工具增加 mTLS 开关和算法 CLI 参数。
- **current behavior**: 目前只能通过配置文件和环境变量覆盖 mTLS/算法。
- **desired behavior**: 支持 `--mtls-enable=0|1`、`--tls-algorithm=<具体算法>`，且命令参数优先。
- **key interfaces**: getopt、TLS options、握手配置、help 和真实工具测试。
- **acceptance criteria**: help 有参数说明；CLI 覆盖测试通过；非法值明确报错；全量测试通过。
- **out of scope**: 不修改协议字段、证书路径、ca_cn 和第二阶段业务帧。
- **information gaps**: 无，用户已确认范围和参数名。
- **dedup results**: T0320 已完成配置/环境变量，本任务只增加 CLI 覆盖层。
- **recommended next steps**: 解析参数并传入现有 TLS options，扩展 help 和集成测试。
