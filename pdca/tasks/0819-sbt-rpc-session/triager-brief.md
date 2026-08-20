# Triage Brief — sbt-rpc-session

- **category**: enhancement
- **scenario_type**: development
- **summary**: 让 dmsbtex、libobk 复用 `rpc_hs_session_t` 的 plain/TLS 传输能力完成 mTLS 后业务收发。
- **current behavior**: SBT 网络代码以 fd 为中心直接调用 socket I/O，已有 RPC session 未接入。
- **desired behavior**: 每个 SBT 连接独立持有 session，协商后统一通过 session 读写，清理 SSL 与 fd 所有权明确。
- **key interfaces**: SBT 连接上下文、plain/TLS session 初始化、业务报文收发、连接销毁。
- **acceptance criteria**: 运行 dmsbtex 构建与测试得到通过；运行 libobk 构建与测试得到通过；运行握手单元测试得到 plain/mTLS/异常路径通过；静态检查得到网络业务路径不绕过 session 且无新增全局锁。
- **out of scope**: 修改 RPC 协议、改变公开 SBT 业务 ABI、迁移非网络 I/O。
- **information gaps**: 当前 xmake 测试目标和证书环境是否完整，需要在 Do 阶段核验并登记 evidence。
- **dedup results**: 已查阅既有 dmsbtex/libobk mTLS 任务及 RPC session 知识；本任务聚焦复用现有 `rpc_hs_session_t` 并完成业务路径迁移，范围不同。
- **recommended next steps**: 完成方案终审与测试接缝确认后，进入 Do 阶段实现并登记构建、单元和集成证据。
