# PRD — 拆分 SBT 系服务端/客户端 mTLS rdb 配置

## 问题陈述

- **现状**：SBT 系（libobk、dmsbtex）的 mTLS 配置中，mtls 开关与算法两个"工具独有"参数当前在"服务端"与"客户端"两种角色之间共用同一组 rdb 配置参数：服务端 TLS 配置初始化与客户端 TLS 配置初始化均读取同一个 mtls 开关参数与同一个算法参数；二者又进一步在 libobk 与 dmsbtex 之间共用。同一运行环境无法为不同模块、不同角色分别设定 mTLS 策略。
- **目标**：让 libobk 与 dmsbtex 各自的"服务端"与"客户端"角色拥有相互独立的 mTLS 配置来源，互不污染。
- **差距**：当前参数注册表中存在"服务端算法"与"客户端算法"两条独立链，但"mtls 开关"仍为 server/client 及 libobk/dmsbtex 共用单一条目；缺少按模块×角色区分的独立配置入口。

## 解决方案

按"模块 × 角色"二维拆分"工具独有"的 mTLS 参数（mtls 开关、算法），为 libobk/dmsbtex 各建立 server/client 四个独立配置 section；证书目录（cert_dir）作为"全局配置"保留不变。完全迁移：删除 SBT 系专属的旧参数名与 env 名，但保留被 RPC 系复用的全局 ini key。

## Seam 分析

### 测试接缝
- 参数注册表层：验证新增四个角色的 mtls/tls_algorithm 参数 ID 解析链独立、旧 ID 已删除、全局 `[security]` key 仍被 RPC 系引用。
- TLS 配置初始化层：验证 libobk/dmsbtex 的 server 与 client 初始化入口各自读取对应角色参数，互不覆盖。
- 握手/集成层：既有 mTLS 集成测试在迁移后行为一致（明文、SM4 mTLS、AES mTLS、缺失证书失败）。
- Mock/Stub：证书材料复用既有测试证书；配置解析通过 env/ini 注入，无需真实网络。

### 声明的测试接缝
- seam: `libs/tests/param_registry_test.c` -> rdb 配置参数注册表
- seam: `libs/tests/rdb_config_test.c` -> rdb 配置参数解析链
- seam: `dmsbtex/test/session_test.c` -> dmsbtex 会话 TLS 配置初始化（server/client）
- seam: `libobk/test/session_test.c` -> libobk 服务端/客户端 TLS 配置初始化

### 验收可测性
- 每个角色参数均可通过 env/ini 独立注入并断言解析结果。
- 互斥场景（server 启用 / client 禁用）可在同一进程分别构造。
- 既有集成测试覆盖明文与 mTLS 路径，可作为回归信号。

## 用户故事

1. 作为 SBT 部署运维，我希望 libobk 服务端与客户端的 mTLS 开关/算法可分别配置，以便两端采用不同策略。
2. 作为 SBT 部署运维，我希望 dmsbtex 服务端与客户端的 mTLS 配置独立，以便分离信任域。
3. 作为 RPC 系运维，我希望 `[security]tls_enable` / `[security]tls_algorithm` 全局兜底配置不受影响，以便既有部署不破坏。
4. 作为测试者，我希望迁移后既有 mTLS 集成测试仍通过，以便确认行为兼容。

## 实现决策

- **新增/修改模块**：rdb 配置参数注册表（新增 8 个参数 ID：libobk_server、libobk_client、dmsbtex_server、dmsbtex_client 各含 mtls_enable 与 tls_algorithm）；SBT 系四个 TLS 配置初始化入口（libobk 服务端、libobk 客户端、dmsbtex 服务端、dmsbtex 客户端）改为读取各自角色参数。
- **接口定义**：每个角色参数 ID 解析链 = 专属 env 名 > `[模块_角色]` section 键 > 兜底/默认。mtls_enable 为 BOOL（仅接受 "0"/"1"，非法 fail-closed）；tls_algorithm 为 STR（白名单 SM4_GCM_SM3 / AES_256_GCM_SHA384，未设置不锁算法）。
- **技术澄清**：cert_dir 保持全局（`[security]cert_dir` / `RPC_TLS_CERT_DIR`），不纳入本次拆分；`[security]tls_enable`、`[security]tls_algorithm` 全局 ini key 保留（继续供 RPC 系 aio-speed/rdbcomm 兜底），SBT 系新参数不引用这两个全局 key。
- **架构决策**：模块×角色四 section 分离（建议记 ADR：SBT mTLS 配置按模块×角色独立）。完全迁移：删除 SBT 专属旧参数 ID（PARAM_SBT_MTLS_ENABLED、PARAM_SBT_TLS_ALGORITHM、PARAM_LIBOBK_CLI_TLS_ALGORITHM）与其 env 名（SBT_MTLS_ENABLE、SBT_TLS_ALGORITHM、LIBOBK_CLI_TLS_ALGORITHM）及注册表中对 `[security]` 层的引用；不保留 SBT 侧兜底，旧 `[security]` 配置对 SBT 系失效，须迁移到新 section。
- **数据模型变更**：参数注册表 enum 增删条目；rdb.conf 示例新增四个 section。
- **API 合约**：TLS 配置初始化入口函数签名不变（仍返回填充的 cfg 结构体），仅内部读取来源变化；CLI 覆盖参数（--mtls-enable/--tls-algorithm）语义不变，映射到对应 server 角色（libobk main、dmsbtex main）。
- **默认值与 fail-closed**：mtls 默认关闭（0）；算法默认未设置（不锁）；非法值拒绝（fail-closed）语义保持。

## 测试决策

- 被测模块：rdb 配置参数注册表、libobk/dmsbtex 的 TLS 配置初始化与握手路径。
- 现有测试先例：libs/tests/param_registry_test.c、libs/tests/rdb_config_test.c、dmsbtex/test/session_test.c、libobk/test/session_test.c。
- 测试定义：仅测外部行为（配置解析结果与握手生效），不测实现细节；同一进程内分别构造 server/client 互斥配置以验证独立性。

## 验收标准

- [ ] AC-1: 参数注册表新增 libobk_server/libobk_client/dmsbtex_server/dmsbtex_client 四个角色的 mtls_enable 与 tls_algorithm 参数 ID，各自解析链独立，单测通过。
- [ ] AC-2: 删除 PARAM_SBT_MTLS_ENABLED、PARAM_SBT_TLS_ALGORITHM、PARAM_LIBOBK_CLI_TLS_ALGORITHM 及其 SBT 专属 env 名（SBT_MTLS_ENABLE、SBT_TLS_ALGORITHM、LIBOBK_CLI_TLS_ALGORITHM）；全局 `[security]tls_enable`、`[security]tls_algorithm` ini key 保留且仍被 RPC 系参数引用。
- [ ] AC-3: libobk 服务端 TLS 配置初始化仅读取 libobk_server 角色参数，libobk 客户端 TLS 配置初始化仅读取 libobk_client 角色参数，同一进程内分别配置得到不同结果、互不覆盖。
- [ ] AC-4: dmsbtex 服务端 TLS 配置初始化读取 dmsbtex_server 角色参数，dmsbtex 客户端 TLS 配置初始化（sbt_session_client_init 路径）读取 dmsbtex_client 角色参数。
- [ ] AC-5: 全局 cert_dir 配置（`[security]cert_dir` / `RPC_TLS_CERT_DIR`）保持不变，SBT 系与 fs-backup 读取行为不变（回归通过）。
- [ ] AC-6: 既有 mTLS 集成测试（dmsbtex/test/session_test.c、libobk/test/session_test.c）在迁移后仍能分别按角色构建并通过握手/明文回归。
- [ ] AC-7: 运行 dmsbtex、libobk、libs 的 xmake build 与 xmake test 全部通过。
- [ ] AC-8: CLI 覆盖（--mtls-enable/--tls-algorithm）仅映射到 server 角色（libobk main、dmsbtex main）；设置旧 SBT 专属 env 名不再影响 SBT 系解析。

## 范围外

- 不改动握手协议字段；不引入新 CLI 参数。
- 不改 RPC 系（aio-speed/rdbcomm）参数配置（其已完成工具级独立配置）。
- 不拆分 cert_dir（全局保留）。
- 不改动 fs-backup 配置读取。
- 不保留 SBT 侧对 `[security]tls_enable`/`[security]tls_algorithm` 的兜底（旧配置须迁移）。

## 备注

- 建议 ADR：SBT mTLS 配置按模块×角色四 section 分离。
- 历史相关任务：0818-tool-mtls-config（RPC 系独立配置，已完成）、0819-dmsbtex-libobk-mtls（mTLS 握手接入，已完成）、0819-sbt-mtls-simplify（证书/算法路径简化，Pending 范围更宽）——本任务聚焦 SBT 系 server/client 的 mtls 开关与算法参数拆分，与其互补不重叠。
- rdb.conf 部署示例需同步新增四个 section 并更新文档。
