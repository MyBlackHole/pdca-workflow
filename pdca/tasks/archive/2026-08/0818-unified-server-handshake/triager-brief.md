# Triage Brief — unified-server-handshake

- **category**: enhancement
- **scenario_type**: development
- **summary**: 将 RPC 与 rdbcomm 服务端重复的首阶段握手和 mTLS 升级流程统一到公共握手入口。
- **current behavior**: RPC 和 rdbcomm 服务端分别读取首帧、处理时间、协商算法并调用 TLS 服务端握手，存在重复和行为漂移风险。
- **desired behavior**: 公共入口统一处理时间请求、错误帧、明文结果和 mTLS 升级；服务端启用 mTLS 时强制要求，未启用时允许明文并接受客户端主动请求 mTLS。
- **key interfaces**: `rpc_hs_session_t`、服务端握手配置、RPC/rdbcomm worker 首阶段入口、TLS session 升级。
- **acceptance criteria**: 运行握手单元和真实 RPC/rdbcomm 集成测试得到时间关闭、明文成功、mTLS 成功、算法错误和服务端强制 mTLS 拒绝结果。
- **out of scope**: 不新增 CLI 参数，不改变现有协议字段，不使用回调，不改变客户端证书 `ca_cn` 选择和 TLS 证书实现。
- **information gaps**: 公共入口是否直接依赖 `tls_cert_server_handshake` 需要在设计中确定；建议通过参数传递配置并由公共层完成 TLS session 绑定。
- **dedup results**: T0315/T0316 已清理遗留协议和辅助函数；本任务专注于重复的服务端握手编排。
- **recommended next steps**: 设计无回调的公共服务端 accept API，接入 RPC/rdbcomm 两个服务端并扩展真实测试。
