# Triage Brief — rpc-net-protocol-cleanup

- **category**: enhancement
- **scenario_type**: development
- **summary**: 清理未被当前 RPC/rdbcomm 协议链路使用的旧 `rpc-net-protocol` 实现。
- **current behavior**: 旧的时间消息序列化文件仍参与 `rpc-net` 静态库编译，并与现行 RPC 协议和握手协议重复定义时间消息。
- **desired behavior**: 删除未使用的旧实现及构建入口，保留现行 `rpc-protocol` 和 `rpc-handshake` 的时间功能。
- **key interfaces**: rpc-net 静态库构建、RPC 时间消息、rdbcomm/RPC 握手时间操作、公共头文件导出。
- **acceptance criteria**: 运行仓库引用扫描得到旧文件名和旧转换函数无内部引用；运行 `xmake build` 得到构建成功；运行 `xmake test` 得到全部测试通过。
- **out of scope**: 不改变现行握手协议、时间操作语义、RPC/rdbcomm API、第三方代码和外部 ABI 兼容策略。
- **information gaps**: 当前仓库无法证明外部二进制是否直接依赖旧 `msg_get_time_*` 符号；本任务按仓库内无外部 ABI 承诺处理，并以完整构建和测试作为边界验证。
- **dedup results**: 未发现当前活跃任务或知识条目正在处理同一清理目标；历史任务仅记录过协议迁移背景。
- **recommended next steps**: 删除旧源文件、移除构建清单和无效 include，扫描引用并执行完整构建测试。
