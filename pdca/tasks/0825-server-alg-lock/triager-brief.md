# Triage Brief — 0825-server-alg-lock

- **category**: enhancement
- **scenario_type**: development
- **summary**: 服务端 tls_algorithm 实施锁定语义（无默认值，显式配置即唯一允许算法），同步消除 rpc cli_algorithm 冗余字段。
- **current behavior**: 四模块协商层忽略配置算法；rpc 存在隐式默认 SM4；cli_algorithm/tls_algorithm 双字段冗余。
- **desired behavior**: 无默认值；显式配置即锁定（其余合法算法回 HS_ERR_ALGORITHM）；未配置不锁保持兼容。
- **key interfaces**: 四模块 config init 的 sec_resolve_str 调用（default 改 NULL）；握手协商函数锁定过滤；cfg.algorithm!=0 作为锁定信号。
- **acceptance criteria**:
  - mixed_mtls_integration 锁定用例：错配拒(HS_ERR_ALGORITHM)/匹配通。
  - libobk/dmsbtex session_test 锁定用例通过。
  - e2e S18/S19：显式锁定服务端拒 AES 放行 SM4。
  - 现有 e2e 全过（无隐式默认兼容证明）。
  - grep 无 cli_algorithm 残留、四模块含 algorithm!=0 过滤分支、default=NULL。
- **out of scope**: 独立拒绝码；客户端侧语义；rdbcomm/dmsbtex/libobk CLI 扩展。
- **information gaps**: rdbcomm server_options 是否已有算法字段待实施时确认。
- **dedup results**: T3960 为本任务前置审查；T0357/T0358 白名单语义为本任务基础。无重复。
- **recommended next steps**: 终审后四模块顺序实施（配置层→协商层→测试→e2e）。
