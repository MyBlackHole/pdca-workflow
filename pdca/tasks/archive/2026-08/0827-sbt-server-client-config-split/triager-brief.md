# Triage Brief — sbt-server-client-config-split

- **category**: enhancement
- **scenario_type**: development
- **summary**: SBT 系（libobk / dmsbtex）的 mTLS 配置当前服务端与客户端的 mtls 开关与证书目录共用同一组 rdb 配置参数，应拆分为服务端独立配置与客户端独立配置。
- **current behavior**: 服务端 TLS 配置初始化与客户端 TLS 配置初始化共用 mtls_enable 开关参数与 cert_dir 证书目录参数；算法参数已有部分分裂（服务端算法 / 客户端算法各自独立），但开关与证书目录仍未拆分。同一运行环境无法为服务端和客户端分别设定不同的 mTLS 开关或证书目录。
- **desired behavior**: 服务端 TLS 配置与客户端 TLS 配置各自拥有独立的 mtls 开关参数、证书目录参数（及一致的参数注册表条目），互不污染；运行时服务端按服务端参数初始化、客户端按客户端参数初始化。
- **key interfaces**: rdb 配置参数注册表（参数 ID 与解析链）、SBT 服务端 TLS 配置初始化入口、SBT 客户端 TLS 配置初始化入口、dmsbtex 服务端 TLS 配置初始化入口。
- **acceptance criteria**:
  - 运行 SBT 服务端配置初始化与客户端配置初始化分别得到各自独立的 mtls 开关与证书目录解析结果，二者互不覆盖。
  - 运行参数注册表单元测试得到服务端参数 ID 与客户端参数 ID 各自存在且解析链正确。
  - 运行 dmsbtex / libobk 构建与既有 mTLS 集成测试得到结果与拆分前一致（行为兼容）。
- **out of scope**: 不改动握手协议字段；不改动算法参数的既有分裂结构（除非统一命名）；不新增与需求无关的 CLI 参数；不修改 RPC 系工具（rdbcomm/aio-speed）的独立配置（其已完成独立配置）。
- **information gaps**: 拆分的具体命名与 ini section 约定；是否需保持对现有 [security]tls_enable / SBT_MTLS_ENABLE / RPC_TLS_CERT_DIR 的向后兼容（旧名是否继续作为兜底）；dmsbtex（当前仅服务端角色）是否也需要客户端配置入口；默认值与 fail-closed 语义是否保持。
- **dedup results**: 已发现 0818-tool-mtls-config（RPC 系工具级独立配置，已完成）、0819-dmsbtex-libobk-mtls（mTLS 握手接入，已完成）、0819-sbt-mtls-simplify（证书/算法路径简化，Pending 但范围更宽）。本任务聚焦 SBT 系 server/client 的 mtls 开关与证书目录参数拆分，未被上述任务覆盖。
- **recommended next steps**: 与用户对齐拆分命名/section 约定、向后兼容策略与范围后，合成完整 PRD。
