# Triage Brief — 0826-dmftp-mtls-cli-args

- **category**: enhancement
- **scenario_type**: development
- **summary**: dm-ftp(dmsbtex) 补齐 --mtls-enable/--tls-algorithm CLI 参数（T3963 审查发现的覆盖面遗漏），复刻 T3959 模式。
- **current behavior**: 仅 env/ini 入口；main 忽略 args_process 返回值；default 分支 exit(0)。
- **desired behavior**: CLI > env > ini 分层；非法值非零退出 fail-closed；与四工具行为一致。
- **key interfaces**: sbt_tls_config_init 签名扩展；getopt 长选项 1004/1005。
- **acceptance criteria**:
  - --help 含新参数说明。
  - 非法值（=2/=abc/TLS_BOGUS）非零退出并输出明确错误。
  - CLI 覆盖 env 行为级证明 + 算法覆盖证明。
  - 不传参数行为不变；dmsbtex_session_test ALL PASS。
- **out of scope**: cert-dir CLI；init_sbt_config 文件路径改造。
- **information gaps**: 无。
- **dedup results**: T3959 为 FileTransferAgent 同构实现，本任务为其在 dm-ftp 的补齐。无重复。
- **recommended next steps**: 直接实施（同构改动，风险低）。
