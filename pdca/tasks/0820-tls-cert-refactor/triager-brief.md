# Triage Brief — tls-cert-refactor

- **category**: enhancement
- **scenario_type**: development
- **summary**: 重构 libs/tls_cert.{c,h}，收敛模块职责为"接收已解析配置→创建 SSL_CTX→加载证书→握手→释放"。
- **current behavior**: 全局单例 g_ctx 仅能承载单一 client/server SSL_CTX；client 通过 tls_cert_select_cert_callback 动态遍历 server 下发 CA 列表猜测证书；存在 CA/host 证书缓存、SM2 与普通分支交织、大量注释掉的死代码与未用接口；配置读取直接依赖环境变量名。
- **desired behavior**: 支持并存的多个 TLS profile（各含算法+ca_cn+证书链，独立 SSL_CTX）；删除动态 CA 列表证书选择回调与目录猜测；删除死代码、注释块与未用接口；整理对外 API 与错误码语义；消除对配置环境变量的直接依赖。
- **key interfaces**: TLS 初始化、SSL_CTX 管理、客户端/服务端握手、证书加载、mTLS 验证。
- **acceptance criteria**: 运行 tls_cert 单元测试与集成握手测试得到成功/失败矩阵通过；运行静态检查与构建得到无动态证书猜测、无未用接口、错误码语义一致。
- **out of scope**: 不修改 RPC 握手报文字段与协议版本；不改变 rdb-config 的 sec_* 配置接口（配置层不动）；不改变 rdbcomm/aio-speed/dmsbtex/libobk 的业务调用方式与 ABI。
- **information gaps**: 调用方（rpc/rpc-io/rpc-client/rpc-handshake/sbt-session/rdbcomm/fs-backup/dmsbtex/libobk）对 tls_cert 公共接口的具体使用方式需盘点确认。
- **dedup results**: 与 T0331「简化 SBT/RPC mTLS 证书与算法路径」概念重合；用户明确选择新建聚焦 tls_cert 模块自身任务，T0331 保持独立 plan。
- **recommended next steps**: 盘点全部调用方接口使用，设计多 profile SSL_CTX 模型与错误码语义，写 prd/design 后进入 Do。