# 实施拆解

## P1：基线与接口盘点

- 对比 `rpc_hs_session_t`、`rpc_io_t`、SBT session 和现有 TLS API 的所有调用者。
- 标记 TIME、NEGOTIATE、业务帧三类路径。
- 列出所有 fd-only TLS/明文入口，确认删除或保留理由。
- 记录当前公开结构和 ABI 约束。

## P2：配置收敛

- 增加统一内部配置结构和严格解析函数，区分服务端 profile 列表与客户端 profile 偏好。
- 固定来源优先级。
- 校验 ca_cn、能力集合和算法名。
- 删除 TLS 层对环境变量名的依赖。
- 增加配置来源、非法值和默认值测试。

## P3：证书加载简化

- 将证书加载改为显式 profile 路径；启动时准备 SM4/AES 两套证书链，握手时按选中 profile 绑定，不允许运行中互相覆盖。
- 删除动态 CA 列表遍历和证书选择回调。
- 将普通证书/SM2 处理收敛为明确算法分支。
- 禁止证书缺失时隐式降级明文。
- 保留证书链和私钥匹配校验。

## P4：握手路径整理

- 保留 TIME 编解码和独立调用路径。
- 保留 NEGOTIATE 编解码和 plain→TLS session 切换。
- 将服务端协商从单一算法改为 PLAIN/SM4/AES 能力集合匹配。
- 增加 PLAIN、SM4、AES 三种并行连接状态和算法不匹配测试。
- 增加“同一服务端同时保有两套 mTLS 证书链”的测试，验证先后建立 SM4/AES 连接不会替换对方 SSL_CTX 或证书。
- 统一客户端/服务端错误返回与 session cleanup。
- 让 aio-speed/rdbcomm/dmsbtex/libobk 业务入口全部持有 session。
- 消除 fd-only mTLS 入口和重复握手实现。

## P5：业务模块接入

- 检查 RPC/rdbcomm 的业务发送和接收是否全部使用 session。
- 检查 dmsbtex/libobk 的业务协议是否全部使用 session。
- 保持公开 SBT/Oracle 结构 ABI 不变。
- 修复连接关闭、重连和业务失败路径的资源释放。

## P6：测试与静态审查

- 配置优先级/非法值测试。
- TIME 独立路径测试。
- NEGOTIATE plain、普通 mTLS、SM2 mTLS、算法不匹配测试。
- 证书缺失、私钥不匹配、握手失败清理测试。
- rdbcomm/aio-speed 业务集成测试。
- dmsbtex/libobk 业务协议集成测试。
- 构建、`git diff --check`、直接 `send/recv`、锁和 fd 映射扫描。

## P7：Check 前证据

- build/test 输出。
- 配置/TLS/握手测试报告。
- 业务集成测试报告。
- 静态检查报告。
- ABI 对比报告。
- 失败场景资源清理审查记录。
