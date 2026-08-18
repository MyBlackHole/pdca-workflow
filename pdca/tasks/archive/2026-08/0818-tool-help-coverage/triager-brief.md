# Triage Brief — 0818-tool-help-coverage

- **category**: enhancement
- **scenario_type**: development
- **summary**: 补充用户可见工具 help 中缺失的参数说明、默认值、约束和可直接运行的使用案例。
- **current behavior**: `aio-speedd`、`rdbcomm`、`rdbcommd`、`tls-keygen`、`fsdeamon` 已有不同程度的 help，但内容粒度、默认值、参数约束和案例不一致；部分 help 没有案例或只列出参数名。
- **desired behavior**: 每个纳入范围的工具都能通过 `--help` 获得完整参数说明、默认值/取值约束、操作关系和至少一个可执行案例；子命令工具的子命令 help 也应覆盖。
- **key interfaces**: 工具命令行入口、getopt 参数表、help 渲染函数、xmake 工具集成测试。
- **acceptance criteria**: 运行每个纳入范围工具的 `--help` 得到所有已注册参数及其含义；运行子命令 `--help` 得到对应子命令参数；运行 help 回归测试得到所有必需参数、默认值、约束和案例标记；运行 `xmake build` 与 `xmake test` 得到成功。
- **out of scope**: 不改变参数名称、短选项映射、业务行为或协议；不新增命令行参数，仅补充已有参数文档；不把内部测试程序作为用户工具纳入范围，除非 Plan 阶段明确加入。
- **information gaps**: 需要确认是否将 `fsdeamon` 纳入统一 help 规范，以及案例是否必须在不启动服务/不修改系统文件的情况下可安全执行。
- **dedup results**: 未命中 `tool-help-documentation` out-of-scope 概念；未发现现有任务专门处理工具 help 覆盖。
- **recommended next steps**: Plan 阶段确认工具范围和案例安全边界；随后按工具分组补齐 help，并将 help 输出作为回归测试断言。
