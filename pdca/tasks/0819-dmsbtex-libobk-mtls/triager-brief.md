# Triage Brief — dmsbtex、libobk 接入 mTLS 握手

- **category**: enhancement
- **scenario_type**: development
- **summary**: 为 dmsbtex↔dm-ftp 与 libobk↔FileTransferAgent 的 SBT TCP 连接接入现有 mTLS 握手能力，并让后续业务帧继续走 TLS 密文 I/O。
- **current behavior**: 两条 SBT 链路直接使用 socket/connect/send/recv/read/write，当前未见 mTLS 握手或 TLS I/O 封装。
- **desired behavior**: 连接建立后按配置完成 mTLS；开启时握手失败、证书不完整或对端不支持均使连接失败且不回退明文；关闭时保持现有明文行为。
- **key interfaces**: SBT 客户端连接初始化、dm-ftp/FileTransferAgent accept 后的会话初始化、协议头收发、业务帧读写、连接清理、现有 tls_cert 初始化与握手接口。
- **acceptance criteria**: 运行 dmsbtex 与 dm-ftp 的真实回归得到 mTLS 握手成功且业务读写成功；运行 libobk 与 FileTransferAgent 的真实回归得到 mTLS 握手成功且业务读写成功；运行缺证书/不匹配/对端不支持场景得到非零失败且无明文降级；运行关闭配置的既有测试得到与基线一致的明文结果。
- **out of scope**: 不改 UI/上层配置页面，不新增 GMSSL 后端，不改 RPC/rdbcomm 协议，不处理 oss HTTPS，不实现旧版本协议兼容之外的额外能力。
- **information gaps**: SBT 两条链路是否共用统一协商头；配置键及默认值需与现有 tls_cert/工具配置约定对齐；FileTransferAgent 与 dm-ftp 的服务端测试启动方式需由现有构建脚本确认。
- **dedup results**: 命中未执行的旧计划 T0257/T0258，以及已完成但范围更大的 T0253；本任务限定为当前代码基线的两条 SBT 链路，作为新的可执行收敛任务。
- **recommended next steps**: 先确认复用现有 tls_cert/OpenSSL mTLS 接口和“关闭默认明文、开启强制失败不降级”的方向，再进入 Do。
