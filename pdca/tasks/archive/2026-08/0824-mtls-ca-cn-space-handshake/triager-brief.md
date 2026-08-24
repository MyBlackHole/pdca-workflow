# Triage Brief — mtls-ca-cn-space-handshake

- **category**: bug
- **scenario_type**: bugfix
- **summary**: aio-speed 客户端 mTLS 握手失败：tls_cert_init_client 对含空格的 CA CN 校验拒绝；且 SM2 证书文件名布局缺回退
- **current behavior**: 服务端协商下发 ca_cn="My SM2 Root CA"（keygen 自带示例名），客户端 tls_cert_ca_cn_valid 白名单 [A-Za-z0-9._-] 不含空格 → ERR_INVALID_PARAM → 握手失败
- **desired behavior**: 含空格的合法 CA CN 可正常完成 mTLS 握手；SM2 算法下证书文件查找具备与 ED25519 对称的回退能力
- **key interfaces**: TLS 客户端证书上下文初始化接口；CA CN 合法性校验；证书文件布局解析（cert_dir/ca_cn/host.* 与算法前缀变体）；tls-keygen 输出布局约定
- **acceptance criteria**:
  - 运行 libs/tests/tls_cert_test 中新增用例：ca_cn 含空格时 build_profile/slot_create 成功得到 Y
  - 运行新增用例：SM2 目录仅有 sm2_host.* 时客户端初始化成功（回退生效）得到 Y
  - 运行 `xmake run aio-speed -h <host> -p <port> -c "ls" --mtls-enable 1` 握手成功执行命令得到 Y
  - 运行既有 tls_cert/rpc_handshake 测试全部保持通过得到 Y
- **out of scope**: 协议层 CN 编码方案重构、keygen 输出布局迁移、服务端逻辑变更
- **information gaps**: 无；根因链已由代码取证锁定
- **dedup results**: 活跃/归档任务无同概念缺陷记录
- **recommended next steps**: Plan 对齐两处修复取舍后进入 Do（TDD：先失败用例再修）
