# Triage Brief — remove-enc-error-codes

- **category**: enhancement
- **scenario_type**: development
- **summary**: 移除项目自定义 `ENC-*` 错误编码，并补充能直接定位 TLS 失败原因的日志。
- **current behavior**: SM2 证书链失败日志包含 `ENC-005`，部分证书初始化失败路径没有说明角色、算法和实际证书路径。
- **desired behavior**: 不再输出自定义 `ENC-*` 编码；错误日志直接包含客户端/服务端角色、算法配置、CA/证书/私钥路径、失败阶段和 OpenSSL 错误原因。
- **key interfaces**: TLS 证书链初始化、客户端/服务端握手、SM2 算法配置、工具集成测试。
- **acceptance criteria**: 运行 `rg 'ENC-[0-9]+' libs rdbcomm rpc` 得到 0 个项目自定义匹配；运行失败测试得到明确角色/路径/算法/原因日志；运行 `xmake test` 全量通过。
- **out of scope**: 不移除 OpenSSL 自身的 `ENC-then-MAC` 文本；不改变 TLS 协议和返回码语义。
- **information gaps**: 需确认现有日志器对多行 OpenSSL 错误队列的输出方式和测试断言位置。
- **dedup results**: T0313 已新增 TLS 握手错误队列日志；本任务只调整错误表达和补充上下文，不重复修复握手逻辑。
- **recommended next steps**: 更新 TLS 证书链错误日志与单测/工具日志断言，随后执行全量回归。
