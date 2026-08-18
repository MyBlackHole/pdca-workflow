# Triage Brief — rdbcomm-rpc-mtls-time

- **category**: enhancement
- **scenario_type**: development
- **summary**: 为 rpc 与 rdbcomm 增加一致的明文握手协商 mTLS 算法，并保留/补齐统一的获取时间协议。
- **current behavior**: rpc 已有独立的 `rpc_get_time` 接口；rdbcomm 连接建立后按现有配置直接进入明文或 TLS，未与 rpc 共享协商协议，也没有获取时间能力。
- **desired behavior**: rpc 与 rdbcomm 在 TLS 前使用同一版本化明文协商协议，按双方能力和配置选择明文或 mTLS 算法；现有 rpc 获取时间行为保持兼容，rdbcomm 提供同协议、同语义的获取时间能力。
- **key interfaces**: 连接建立、协商请求/响应、mTLS 算法能力声明、明文/TLS 数据面切换、获取时间请求/响应。
- **acceptance criteria**: 运行协议编解码与判定测试得到 rpc/rdbcomm 对同一协商报文产生一致结果；运行明文握手集成测试得到两模块均能完成明文连接；运行 mTLS 算法能力测试得到双方支持时升级成功且不支持时失败不降级；运行时间协议测试得到 rpc 与 rdbcomm 返回一致格式和非零时间戳；运行既有 rpc 时间回归得到原有调用继续通过。
- **out of scope**: 不重新实现底层 TLS/mTLS 后端、证书签发、其他工具链路适配或业务层时间校准策略。
- **information gaps**: 协商报文的最终字段/版本、rdbcomm 时间消息的兼容方式、mTLS 算法配置来源和默认值、旧客户端无协商头的兼容策略、测试接缝需在 Plan 对齐。
- **dedup results**: T0260 已覆盖 RPC 协商方向但未覆盖 rdbcomm 与统一时间协议；无同范围重复任务；相关 GMSSL/mTLS 知识已存在。
- **recommended next steps**: 完成逐轮 Grill，明确统一协议和兼容边界，产出 PRD、测试接缝与子任务后请求最终方案确认。
