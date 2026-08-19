# Triage Brief — rpc-rdbcomm-sm2-app-frame-followup

- **category**: bug
- **scenario_type**: development
- **summary**: 修复 rdbcomm 使用 SM2/TLS_SM4_GCM_SM3 时真实应用帧在握手后失败的问题。
- **current behavior**: SM2 证书与密码套件初始化成功，TIME-only 可完成，但真实 rdbcomm 应用请求在 TLS 握手后返回失败；服务端只记录 TLS handshake failed。
- **desired behavior**: rdbcomm 与 RPC 使用相同的 SM2 mTLS session 读写路径，完成真实应用数据帧往返；失败时保留明确的错误边界，不降级为明文。
- **key interfaces**: 第一阶段协商、ca_cn 证书选择、TLS session 读写、rdbcomm 应用帧、RPC/rdbcomm 工具集成测试。
- **acceptance criteria**: 运行真实 rdbcommd/rdbcomm SM2 mTLS 应用测试得到成功请求和响应；运行错误场景得到非零退出与连接关闭；运行 `xmake test` 得到全量通过。
- **out of scope**: 不新增 CLI 参数、不兼容旧协议、不引入裸 fd 到业务层的适配。
- **information gaps**: 现有服务端/客户端没有输出足够的 OpenSSL 错误栈，需要补充诊断并确定失败发生在证书验证、密码套件协商还是 session 切换。
- **dedup results**: T0312 已覆盖基础工具矩阵并明确该缺口；本任务是其唯一跟进，不重复已有 TIME/classic mTLS 工作。
- **recommended next steps**: 先在真实 SM2 失败路径采集 OpenSSL 错误队列和协商结果，再以最小修复完成 session 绑定和应用帧回归测试。
