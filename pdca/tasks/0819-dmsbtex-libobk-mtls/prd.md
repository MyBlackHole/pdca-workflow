# dmsbtex、libobk 接入 mTLS 握手 — PRD

## 问题陈述

- **现状**：dmsbtex↔dm-ftp 和 libobk↔FileTransferAgent 的 SBT 传输仍直接使用裸 TCP；连接及业务包没有统一的 mTLS 会话对象，业务读写无法保证经过 TLS。
- **目标**：两条 SBT 链路都能在同一连接上完成 mTLS 握手，并让握手后的协议头、业务数据和关闭流程使用同一 TLS 会话；配置关闭时保持现有明文路径。
- **差距**：客户端连接、服务端 accept、协议收发和资源清理均以 fd 为中心，尚未接入 TLS 状态、证书验证、握手错误传播和 TLS I/O。

## 解决方案

抽取或复用现有 `tls_cert` 的客户端/服务端证书上下文与握手接口，在 dmsbtex、libobk 两条链路的连接初始化处建立 SBT transport session。session 同时持有 fd 与可选 SSL 对象，并提供完整读、写、收包、发包和清理操作。连接建立先按双方配置协商是否启用 mTLS；启用时握手或证书校验失败立即关闭连接并返回明确错误，不得回退明文；关闭时继续使用明文 transport。

## Seam 分析

### 测试接缝

- 客户端接缝：dmsbtex SBT 连接初始化、libobk SBT 连接初始化。
- 服务端接缝：dm-ftp 与 FileTransferAgent accept 后的会话初始化及清理。
- 传输接缝：协议头和业务 body 的完整读写、部分读写、TLS 错误传播。
- 集成接缝：两组真实客户端/服务端进程在明文、mTLS、失败配置下的结果。

### 声明的测试接缝

- seam: libs/tests/sbt_transport_test.c -> libs/sbt_transport.c
- seam: dmsbtex/network.c -> libs/sbt_transport.c
- seam: libobk/lib/logic/oracleCmdTbl.c -> libs/sbt_transport.c

### 验收可测性

每个模式均以进程退出码、握手日志、业务 payload 回显/文件结果和抓包或 I/O 计数判定。失败场景必须同时验证连接失败与未执行明文业务写入；明文回归必须验证协议结果与当前基线一致。

## 用户故事

1. 作为 DBA，我希望 dmsbtex 的备份数据在启用 mTLS 时经证书双向认证后传输。
2. 作为 DBA，我希望 libobk 的备份/恢复业务帧在启用 mTLS 后仍能正常收发。
3. 作为运维人员，我希望证书缺失、校验失败或对端不支持时任务明确失败，不发生静默明文降级。
4. 作为存量用户，我希望关闭 mTLS 时现有明文链路不受影响。

## 实现决策

- 复用现有 `tls_cert` 的证书加载、客户端握手和服务端握手能力，不在本任务新增 TLS 后端或重新实现证书校验。
- 两条 SBT 链路使用统一的 transport/session 语义，避免业务层在 mTLS 连接上继续调用裸 fd `read/write/send/recv`。
- mTLS 开关沿用当前工具配置体系；默认关闭保持兼容，显式开启即强制，任何协商/握手/证书错误均失败不降级。
- 连接清理必须唯一负责 SSL shutdown/free 与 fd close，失败路径同样释放已建立的 SSL 对象。
- 协商头只承担能力与模式选择；TLS 握手完成后不再发送明文业务数据。

## 测试决策

- 单元/接缝测试覆盖 transport 的模式选择、部分读写、握手失败和 cleanup。
- 真实进程测试分别覆盖 dmsbtex↔dm-ftp、libobk↔FileTransferAgent 的明文和 mTLS 业务路径。
- 失败矩阵至少包含缺少客户端证书、服务端证书/CA 不可用、证书不匹配、对端不支持 mTLS。
- 运行现有工程构建及测试，确认未启用 mTLS 的已有 SBT 行为无回归。

## 验收标准

- [ ] AC-1: 运行 dmsbtex↔dm-ftp mTLS 集成测试，得到握手成功、双向证书校验成功且至少一个真实 SBT 业务帧成功。
- [ ] AC-2: 运行 libobk↔FileTransferAgent mTLS 集成测试，得到握手成功、双向证书校验成功且至少一个真实 SBT 业务帧成功。
- [ ] AC-3: 静态检查与接缝测试证明 mTLS 会话建立后协议头和业务 body 均通过 TLS I/O，不再绕过 session 使用裸 fd 读写。
- [ ] AC-4: 运行缺证书、证书不匹配和对端不支持场景，客户端以非零结果失败并产生可诊断错误，抓包/服务端记录证明未回退明文业务传输。
- [ ] AC-5: 运行 mTLS 关闭的 dmsbtex、libobk 现有回归，协议结果与基线一致且不要求证书配置。
- [ ] AC-6: 运行构建和相关测试，dmsbtex、libobk 及其服务端目标均成功编译，既有压缩、校验和连接清理测试无回归。

## 范围外

- UI、上层作业配置页面和配置中心改造。
- RPC/rdbcomm、oss HTTPS、tls_keygen、GMSSL/TLCP 后端或国密证书签发链改造。
- 旧协议版本兼容策略以外的新协议特性和性能专项优化。

## 备注

旧计划 T0257/T0258 曾提出更大的 SBT 国密 TLS 方案，但未进入 Do；本 PRD 以当前仓库已有 `tls_cert` mTLS 能力为前提，先完成两条链路的可运行接入与回归。
