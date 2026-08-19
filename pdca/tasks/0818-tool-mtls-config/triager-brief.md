# Triage Brief — 0818-tool-mtls-config

- **category**: enhancement
- **scenario_type**: development
- **summary**: 为 rdbcomm 与 aio-speed 客户端增加 mTLS 开关和算法参数，并让两个工具拥有独立配置来源。
- **current behavior**: 两个客户端已经有握手配置 API，但高层连接逻辑主要从共享安全配置读取 mTLS 开关和算法；无法为 rdbcomm 与 aio-speed 分别设置不同策略。
- **desired behavior**: 每个工具可独立配置是否请求 mTLS、算法类型及相关证书配置；工具将独立配置转换为显式握手配置，明文/mTLS 和 CLASSIC/SM 算法选择可被测试验证。
- **key interfaces**: 工具配置加载、客户端连接配置、mTLS 证书初始化、RPC/rdbcomm 握手配置结构、配置优先级和工具集成测试。
- **acceptance criteria**: 运行 rdbcomm 与 aio-speed 的独立配置测试得到各自 mTLS 开关和算法生效；运行配置优先级测试得到工具配置不互相污染；运行明文、经典 mTLS、SM2 mTLS 工具测试得到成功或明确错误；运行 `xmake build` 与 `xmake test` 得到成功。
- **out of scope**: 不修改握手协议字段、不改变第二阶段业务帧、不新增与需求无关的 CLI 参数、不改变服务端证书按 `ca_cn` 选择逻辑。
- **information gaps**: 需要确认“参数”是现有 CLI 参数、配置文件项、环境变量，还是三者组合；需要确认独立配置是独立配置文件还是同一文件不同 section；需要确认 rdbcomm 与 aio-speed 的默认值和优先级。
- **dedup results**: 已发现历史任务已完成握手协议、TLS session 和客户端 API 基础实现；本任务聚焦工具级独立配置，未命中同概念 out-of-scope。
- **recommended next steps**: Plan 阶段确认配置载体、section/file 组织、优先级和默认策略；再设计两个工具到统一握手配置结构的适配接缝。
