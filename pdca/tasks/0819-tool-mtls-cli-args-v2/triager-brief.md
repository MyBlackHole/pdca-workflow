# Triage Brief — 0819-tool-mtls-cli-args-v2

- **category**: enhancement
- **scenario_type**: development
- **summary**: 为 rdbcomm、rdbcommd、aio-speed、aio-speedd 增加 mTLS 开关和算法 CLI 参数。
- **current behavior**: 工具仅支持配置文件和环境变量，命令行无法临时覆盖工具 mTLS/算法策略。
- **desired behavior**: 四个工具支持 `--mtls-enable=0|1` 与 `--tls-algorithm=<具体算法>`，命令参数优先于其他配置。
- **key interfaces**: getopt 参数解析、工具 TLS 初始化、RPC/rdbcomm 握手配置、help 输出和真实工具测试。
- **acceptance criteria**: 运行四个工具 help 得到参数说明；运行 CLI 覆盖测试得到命令参数优先于环境/配置；运行全量测试通过。
- **out of scope**: 不修改握手协议字段、证书路径、ca_cn 选择逻辑和第二阶段业务帧。
- **information gaps**: 无；用户已确认四工具和参数命名。
- **dedup results**: T0320 已完成 help、宏和配置/环境变量；本任务只增加 CLI 覆盖层。
- **recommended next steps**: 增加参数状态对象，解析后传入现有 TLS options API，并扩展 help 与真实工具测试。
