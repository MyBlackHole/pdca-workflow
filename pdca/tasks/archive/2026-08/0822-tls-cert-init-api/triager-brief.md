# Triage Brief — tls-cert-init-api

- **category**: enhancement
- **scenario_type**: development
- **summary**: 完善 libs/tls_cert 初始化 API：服务端通过 cert_dir 自动构建 SM4+AES 双算法证书链，客户端通过 cert_dir + algorithm（工具参数 hs_algorithm_name）+ ca_cn（握手协商结果）构建路径；移除显式 profiles 数组兼容路径，不兼容旧写法。
- **current behavior**: `libs/tls_cert.{c,h}` 已具备 cert_dir 驱动的 `tls_cert_build_server_profiles` / `tls_cert_build_client_profile` 及便捷初始化 `tls_cert_init_{server,client}_from_cert_dir`，`tls_cert_init_{server,client}` 内部已支持 cert_dir 分支；但服务端调用点（`rpc/main.cpp:413`、`rdbcomm/rdbcommd-main.c:352`）在 cert_dir 存在时才走双算法，cert_dir 为空时仍单 profile 回退；客户端 `rpc/rpc-io.cpp:133` 存在 cert_dir 与显式路径双分支重复逻辑且涉及栈局部指针组装。
- **desired behavior**: tls_cert 对外 API 仅 `cert_dir` 驱动唯一路径（服务端 `{mtls_enabled, cert_dir}` 双算法全量，客户端 `{mtls_enabled, cert_dir, algorithm, ca_cn}` 三元组），移除显式 `profiles[2]` 兼容分支；全部调用点强制 `cert_dir`。
- **key interfaces**: `tls_cert_server_options_t{mtls_enabled, cert_dir}`、`tls_cert_client_options_t{mtls_enabled, cert_dir, algorithm, ca_cn}`、`tls_cert_build_server_profiles`、`tls_cert_build_client_profile`、`tls_cert_init_server/client/_from_cert_dir`、握手按 `algorithm` 选 profile。
- **acceptance criteria**: 服务端 cert_dir 双算法与客户端 cert_dir+algorithm+ca_cn 单路径成功/失败矩阵可测；旧 `profiles` 显式分支已移除且编译期不通过；调用点无残留。
- **out of scope**: 不改握手帧格式与协议版本；不改 `rdb-config` sec_* 签名；不引入证书自动轮转/重载。
- **information gaps**: `cert_dir` 默认值 `DEFAULT_CERT_DIR` 与环境变量 `RPC_TLS_CERT_DIR` 的统一解析已在调用点落地；`cert_dir/algorithm/ca_cn` 缺失时统一 `INVALID_PARAM` 不降级明文，已在 PRD 技术澄清明确（已闭环）。
- **dedup results**: 与 T0332 `0820-tls-cert-refactor` 概念近似但本任务聚焦“初始化 API 的 cert_dir + 双算法 + algorithm/ca_cn 固化与调用点收敛”；T0332 已 Completed，本任务为其后续增量；与 `0821-tls-cert-ssl-wrapper` 等无重叠。
- **recommended next steps**: 补齐 PRD Seam/验收，明确 seam 契约，完善服务端/客户端 cert_dir 构建的返回与错误码语义，清理 rpc-io 重复分支，增量测试覆盖双算法 cert_dir 路径。
