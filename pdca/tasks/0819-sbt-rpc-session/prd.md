# dmsbtex/libobk复用rpc会话传输

## 问题陈述

- **现状**: dmsbtex 与 libobk 的网络层和业务函数普遍直接使用 socket fd 调用 `send/recv`；当前仓库已有 `rpc_hs_session_t`，但两个 SBT 模块尚未复用其 plain/TLS 传输能力。
- **目标**: 将 `rpc_hs_session_t` 嵌入 SBT 连接上下文，复用其明文/TLS 读写函数和 SSL 生命周期管理，并完成 dmsbtex、libobk 的业务网络收发迁移。
- **差距**: 连接建立、mTLS 协商、业务报文收发和释放路径仍以 fd 为中心，无法保证 mTLS 协商后所有业务 I/O 都走 `SSL_read/SSL_write`。

## 解决方案

在 dmsbtex 与 libobk 的连接状态中持有 `rpc_hs_session_t`。连接建立后先初始化 plain session，调用已有 RPC 握手协商接口；选择 mTLS 后在同一 fd 上完成 TLS 握手，再用 `rpc_hs_session_init_tls()` 切换会话读写回调。SBT 保留自己的业务报文头和协议解析，仅替换底层字节流收发。

不新增全局 fd 映射、slot 或互斥锁；每个连接独立持有 session。清理时调用 `rpc_hs_session_cleanup()` 释放 SSL，再由连接所有者关闭 fd。

## Seam 分析

### 测试接缝

- dmsbtex 连接/报文 I/O 接口：验证 plain 与 mTLS session 下 SBT 报文收发行为。
- libobk SBT 连接/Oracle 命令收发接口：验证连接建立、业务请求和释放路径使用 session。
- 现有 `rpc_hs_session_t` 握手与 TLS 单元测试：复用并补充 session 切换、错误清理验证。
- 测试采用 socketpair/本地测试服务隔离网络；真实工具矩阵作为集成验证，证书配置缺失时明确报告不可执行。

### 声明的测试接缝

- seam: `dmsbtex/test/test.c` -> `dmsbtex/network.c`, `dmsbtex/sbt.c`
- seam: `libobk/test/test.c` -> `libobk/lib/sbt/libobk.c`, `libobk/lib/logic/oracleCmdTbl.c`
- seam: `libs/tests/rpc_handshake_test.c` -> `libs/rpc-handshake.c`

## 用户故事

1. 作为 dmsbtex 使用者，我希望 SBT 业务报文在 mTLS 协商后继续正常收发。
2. 作为 libobk 使用者，我希望 Oracle 备份命令复用统一 session 传输且不改变公开业务 ABI。
3. 作为维护者，我希望每个连接独立管理 TLS 状态，不依赖全局锁或 fd 查找表。

## 实现决策

- `rpc_hs_session_t` 作为 SBT 连接上下文的内部成员，不直接替换 dmsbtex/libobk 的公开业务 API。
- SBT 业务层不直接使用 RPC 的业务帧函数；只复用 session 的 read/write 回调、初始化和清理能力。
- dmsbtex/libobk 的网络函数改为接收连接上下文或 session 指针，避免 mTLS 路径重新退回裸 fd。
- 保留文件读写、pipe 读写等非 socket I/O 的原有系统调用。
- 明确 fd 所有权：session cleanup 释放 SSL，不关闭 fd；连接销毁路径负责关闭 fd 且只执行一次。

## 测试决策

- 单元层覆盖 plain/TLS session 初始化、回调切换、握手失败清理。
- 模块层覆盖 dmsbtex/libobk 业务报文的完整收发，不只验证握手成功。
- 集成层覆盖客户端/服务端 mTLS 开关和算法组合；环境不可用时记录阻塞证据，不伪造通过。

## 验收标准

- [ ] AC-1: 运行 dmsbtex 的构建与测试目标，得到包含 `rpc_hs_session_t` session 初始化、业务收发和清理路径的通过结果。
- [ ] AC-2: 运行 libobk 的构建与测试目标，得到 Oracle SBT 业务请求/响应经 session 传输的通过结果。
- [ ] AC-3: 运行 RPC handshake 单元测试，得到 plain、mTLS、算法不匹配和错误清理用例通过结果。
- [ ] AC-4: 静态检查 dmsbtex/libobk 网络路径，得到业务 socket 收发不再绕过 session 直接调用 `send/recv` 的结果。
- [ ] AC-5: 静态检查连接状态，得到不存在全局 fd-to-session 映射或新增 pthread mutex 的结果。

## 范围外

- 不修改 RPC 握手报文字段和现有 RPC 业务协议。
- 不改变 dmsbtex/libobk 对外暴露的 Oracle/SBT 业务函数签名。
- 不迁移文件、pipe、eventfd 等非网络 I/O。
- 不删除现有 pthread 用于线程创建、信号屏蔽或服务生命周期的代码；仅禁止为 session 映射新增锁。

## 备注

RPC 迁移提交 `df6b6145`、`5d1a9d92` 和 `0356fb14` 作为实现参考。重点检查所有业务分支，而不是只检查握手入口。
