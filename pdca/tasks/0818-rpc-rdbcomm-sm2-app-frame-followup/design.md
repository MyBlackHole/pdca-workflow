# T0313 design

采用真实工具进程作为主测试接缝：使用现有 SM2 证书和 `RPC_TLS_CIPHERSUITES=TLS_SM4_GCM_SM3` 启动 rdbcommd/rdbcomm，先验证第一阶段协商、服务端返回的 `ca_cn`、TLS 握手和应用帧读写的每个边界。

实现上保持 `rpc_hs_session_t` 的 SSL、read、write 三者生命周期绑定。诊断信息只在握手失败路径记录 OpenSSL 错误队列、协议版本和密码套件，不把明文 fd 重新交给应用层。修复后补充成功和失败断言，并回归 RPC、classic mTLS、TIME-only 及全量 xmake test。

备选方案是绕过 rdbcomm 工具改写为内存 BIO 单测；该方案不能证明真实配置、ca_cn 选择和工具进程环境，故不采用。
