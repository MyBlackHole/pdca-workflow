# Triage Brief — rpc-legacy-helper-cleanup

- **category**: enhancement
- **scenario_type**: development
- **summary**: 清理 RPC 网络模块中未使用的旧辅助函数，并移除已被实际调用函数上的无效 `unused` 属性。
- **current behavior**: `libs/rpc-net.c` 保留未调用的旧原始 fd 收发函数；`libs/tls_keygen.c` 的多个实际调用函数仍带 `unused` 属性；`tls_cert_verify_is_local` 无活动调用但仍是公共 API。
- **desired behavior**: 删除确定无调用的内部辅助函数，清理错误属性；对公共 API 只完成依赖审查，不在无 ABI 决策时删除。
- **key interfaces**: rpc-net 会话 I/O、tls-keygen 子命令处理、TLS 证书公共 API。
- **acceptance criteria**: 运行调用关系扫描得到内部旧辅助函数无引用；运行编译和完整测试得到成功；运行属性扫描确认实际调用的 tls-keygen 函数不再标记 unused。
- **out of scope**: 不删除可能被外部使用的 `tls_cert_verify_is_local` 公共 API；不修改 RPC/rdbcomm 协议和第三方代码。
- **information gaps**: 仓库外部是否依赖 `tls_cert_verify_is_local` 无法由源码确认，因此保留并单独记录。
- **dedup results**: T0315 已清理旧 `rpc-net-protocol` 文件；本任务仅处理同文件中遗留辅助函数和相邻属性问题。
- **recommended next steps**: 删除两个 `libs/rpc-net.c` 静态函数，移除 tls-keygen 实际调用函数的 unused 属性，执行构建、测试和符号扫描。
