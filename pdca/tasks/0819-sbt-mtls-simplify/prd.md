# 简化 SBT/RPC mTLS 证书与算法路径

## 问题陈述

当前 mTLS 实现同时承担配置优先级、证书发现、CA 列表选择、SM2 兼容、算法推断和 TLS 生命周期管理。需求已经明确传递 `ca_cn` 与算法名，不再需要历史证书布局和动态猜测逻辑；现有复杂实现增加了失败路径、资源释放和可观测性风险。

## 目标方案

- 配置层产生经过白名单校验的 TLS profile 列表和客户端 profile 偏好；服务端可同时持有明文、SM4 mTLS、AES mTLS 三种状态及其各自证书链。
- TLS 层按选中的 profile 加载确定证书目录和文件，不扫描目录、不动态猜测客户端证书；不同 profile 的证书链相互独立、可同时存在。
- RPC 一阶段保留 `TIME` 与 `NEGOTIATE` 两个并列操作；`NEGOTIATE` 负责 mTLS 协商和 session plain→TLS 切换，`TIME` 保持独立的时间请求/响应流程；SBT 只复用 session。
- 所有客户端/服务端失败出口统一清理 session、SSL、fd 和私有上下文。
- 删除 fd-only 的隐式 TLS 兼容路径，所有需要 mTLS 的调用使用 session API。

## 范围

涉及 `rdb-config`、`tls_cert`、`rpc-handshake/rpc-io`、rdbcomm/aio-speed 以及 dmsbtex/libobk 的 mTLS 接入和测试。保留普通证书与 SM2 两种明确算法分支，但不保留历史兼容目录或模糊算法匹配。

## 验收标准

- [ ] AC-1: 运行配置测试，得到 CLI > 模块环境变量 > 模块配置 > 全局配置 > 默认值的稳定优先级，并拒绝非法 ca_cn、算法和能力集合。
- [ ] AC-2: 运行 TLS 单元测试，得到服务端同时加载并保有 PLAIN、TLS_SM4_GCM_SM3、TLS_AES_256_GCM_SHA384 三个 profile；SM4/AES 分别使用各自 ca_cn 和证书链，并覆盖单 profile 缺失和算法不匹配失败结果。
- [ ] AC-3: 运行 RPC/rdbcomm/aio-speed 测试，得到 `TIME` 与 `NEGOTIATE` 作为并列一阶段操作分别通过；同一服务端在不重启、不替换证书上下文的情况下可分别建立 PLAIN、SM4 mTLS、AES mTLS 连接，业务路径使用对应 session。
- [ ] AC-4: 运行 dmsbtex/libobk mTLS 集成测试，得到业务报文按选中 profile 经过 TLS session 收发，握手失败和业务失败均完成资源清理。
- [ ] AC-5: 运行静态检查和构建，得到无目录扫描/动态证书猜测、无重复握手实现、无新增全局锁或 fd 映射，并且核心目标构建通过。

## Seam 分析

### 声明的测试接缝

- seam: `libs/tests/rdb_config_test.c` -> 配置优先级与参数校验
- seam: `libs/tests/tls_cert_test.c` -> 确定证书链加载与 TLS 初始化
- seam: `libs/tests/rpc_handshake_test.c` -> session 协商、TLS 切换和清理
- seam: `rdbcomm/tests/tool_integration.c` -> rdbcomm 客户端/服务端 mTLS 业务路径
- seam: `dmsbtex/test/session_test.c` -> dmsbtex session 业务报文收发
- seam: `libobk/test/protocol_test.c` -> libobk Oracle 业务协议 session 收发

## 不在范围内

- 不修改 RPC 握手报文字段和协议版本。
- 不保留历史证书目录、旧算法别名、旧 fd-only TLS 接口的行为兼容。
- 不引入锁或全局 fd→session 映射。
