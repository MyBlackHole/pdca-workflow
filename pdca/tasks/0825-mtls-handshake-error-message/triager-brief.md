# Triage Brief — 0825-mtls-handshake-error-message

- **category**: bug
- **scenario_type**: bugfix
- **summary**: 服务端强制 mTLS 拒绝明文客户端时，客户端报错只有十六进制错误码（如 result=0x8004）甚至静默失败，需翻译为可读文案并覆盖全部四个模块。
- **current behavior**: rpc 客户端打印 `server rejected: handshake error result=0x8004` 且退出码被截断为无意义的 252；libobk 打印 `result=0x%x`；rdbcomm 客户端握手被拒时静默返回 -1 无日志；dmsbtex 客户端只打笼统 "SBT session handshake failed" 不带服务端错误码。
- **desired behavior**: 客户端收到握手错误码后输出明确原因（如 "server requires mTLS but client TLS is disabled; enable tls/cert_dir in config"），rdbcomm 静默失败点补充日志；各模块对 0x8001~0x8008 全部错误码均有可读映射。
- **key interfaces**: 各模块握手协议错误码表（四套前缀语义一致）；客户端响应循环中的握手帧防御分支；客户端主动握手失败路径；进程退出码传递。
- **acceptance criteria**:
  - 运行"服务端强制 mTLS + 客户端未启用 TLS + aio-speed 执行命令"，stderr 含 "mTLS required" 类可读文案（不再是裸十六进制码）。
  - 运行同场景 libobk/rdbcomm/dmsbtex 客户端用例，日志均含可读拒绝原因（rdbcomm 不再静默）。
  - 运行正常象限（plain/mixed/forced 通）回归，无报错文案回归。
  - grep 确认四模块客户端代码中不再有裸 `%x` 打印握手结果码的路径（均有码→文案转换）。
- **out of scope**: 握手协议帧格式变更；自动重试；服务端侧报错改造（服务端文案已可读）。
- **information gaps**: 错误码转文案函数的落点（各模块独立 vs libs 统一）；退出码修正是否纳入本任务。
- **dedup results**: 与 0822-rpc-hs-err-exit-code（误解析+退出码修复）不重复，本任务聚焦文案可读性；0823-cross-module-review 的错误码归一建议与本任务相关但独立。out-of-scope 库无命中。
- **recommended next steps**: Plan 阶段澄清码表落点与退出码范围后合成完整 PRD；测试沿用 mixed_mtls_integration 场景扩展断言 stderr 文案。
