# Triage Brief — 0825-fta-mtls-cli-args

- **category**: enhancement
- **scenario_type**: development
- **summary**: FileTransferAgent（dm-ftp 传输代理服务端）缺少 mTLS/算法 CLI 参数，补齐与 aio-speedd/rdbcommd 一致的 --mtls-enable/--tls-algorithm 覆盖能力。
- **current behavior**: mTLS 配置仅 env(SBT_MTLS_ENABLE/SBT_TLS_ALGORITHM)/ini 分层；sbt_server_tls_config_init 签名无 CLI 入口。
- **desired behavior**: CLI > env > ini 分层；CLI 非法值报错退出（fail-closed）；启动日志输出 TLS 状态。
- **key interfaces**: sbt_server_tls_config_init 签名扩展；getopt 长选项；算法白名单（SM4_GCM_SM3/AES_256_GCM_SHA384）。
- **acceptance criteria**:
  - 运行 --help 含新参数说明。
  - 运行非法值场景（--mtls-enable=2、--tls-algorithm=TLS_BOGUS）非零退出并输出明确错误。
  - 运行合法 mTLS 启动场景，日志含 mTLS enabled 与所选算法。
  - 不传新参数行为不变；libobk_session_test 回归通过。
- **out of scope**: cert-dir CLI；协议帧变更；客户端侧改造。
- **information gaps**: 无。
- **dedup results**: 无同主题任务（T0394 为 rdbcomm mTLS，T0352 为 rpc 混合矩阵，均不覆盖 FileTransferAgent CLI）。
- **recommended next steps**: 按方案实施；e2e 新增 FTA 场景验证 CLI 行为。
