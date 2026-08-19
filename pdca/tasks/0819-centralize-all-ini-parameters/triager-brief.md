# Triage Brief — 0819-centralize-all-ini-parameters

- **category**: enhancement
- **scenario_type**: development
- **summary**: 由 `libs/rdb-config.c/h` 统一定义、读取、默认化、覆盖和校验范围内全部 INI 参数。
- **current behavior**: INI 文档解析已集中，但各 app 仍分别维护参数映射、默认值、重载入口和部分语义。
- **desired behavior**: 共享配置模块拥有全部 INI 参数元数据和归一化结果；app 只消费统一配置结果，不再维护 INI 参数语义。
- **key interfaces**: 参数描述表、统一配置快照、类型化读取、环境变量覆盖、校验、展示和重载生命周期。
- **acceptance criteria**: 运行配置回归测试得到所有范围内 section/key/default/priority 与基线一致；运行源码扫描得到 app 不再实现 INI 参数解析/默认值/校验；运行全量构建和测试得到全部通过。
- **out of scope**: xbsa、不改变 INI 文件格式、业务协议、TLS/mTLS 握手、业务运行时校验和命令行参数语义。
- **information gaps**: 需要在 Plan 中盘点所有当前 INI 参数并确定统一快照的字段边界。
- **dedup results**: T0324 只完成共享 INI 文档和基础 API，本任务继续收敛参数定义与生命周期，非重复实现。
- **recommended next steps**: 建立参数清单和基线测试，设计统一参数描述/快照 API，分批迁移 RPC、fs-backup、s3tools 和安全配置。
