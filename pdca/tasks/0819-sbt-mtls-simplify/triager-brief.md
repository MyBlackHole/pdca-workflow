# Triage Brief — sbt-mtls-simplify

- **category**: enhancement
- **scenario_type**: development
- **summary**: 移除不需要的历史兼容和动态证书选择逻辑，按明确 ca_cn 与算法名实现单一路径 mTLS。
- **current behavior**: TLS 配置、证书选择、算法识别、SM2 兼容和多级来源混杂在多个入口，证书加载路径与握手策略不够确定。
- **desired behavior**: 服务端配置并行支持 PLAIN、TLS_SM4_GCM_SM3、TLS_AES_256_GCM_SHA384，客户端按偏好选择；TLS 层按确定 ca_cn 和选中算法加载证书链；TIME 与 NEGOTIATE 保持并列的一阶段操作；RPC/SBT 业务层只使用 session。
- **key interfaces**: 配置解析、rpc_hs_session_t、TLS 证书初始化、客户端/服务端握手、SBT 业务传输。
- **acceptance criteria**: 运行配置单元测试得到 ca_cn/算法非法值拒绝且来源优先级稳定；运行 mTLS 集成测试得到普通证书和 SM2 证书的成功/失败矩阵通过；运行构建与静态检查得到无动态证书猜测、无重复握手实现、session 清理完整。
- **out of scope**: 不保留旧证书目录布局、旧算法别名、旧 fd-only TLS 行为或隐式明文降级；不修改 RPC 握手报文格式。
- **information gaps**: 当前 SBT 证书目录的最终部署规范需按现有 ca_cn 目录约定固定；需要补充 SBT 真实 mTLS 集成测试。
- **dedup results**: 已有 T0330 负责 SBT 接入 rpc session；本任务只处理其审查发现的 TLS 证书/算法复杂度和失败清理问题。
- **recommended next steps**: 完成 Plan 方案确认后，统一配置模型，简化 tls_cert，补充失败清理和 SBT mTLS 测试，再进入 Check。
