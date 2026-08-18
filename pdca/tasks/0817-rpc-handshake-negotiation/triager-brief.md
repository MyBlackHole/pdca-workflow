# Triage Brief — RPC 层自定义握手包协商

## 分类

- **category**: enhancement
- **scenario_type**: development

## 需求来源

用户（PDCA 流程驱动）："继续开发下一个内容，比如 rpc 支持通过自定义握手包来确定是否进行安全通信"

## 查重结果

- 父任务 T0253（备份复制传输加密）已拆 6 个子任务（T0254 tls_cert 双后端、T0255 tls_keygen SM2、T0256 配置开关、T0257 dmsbtex、T0258 libobk、T0259 oss），**均不含 RPC 层（aio-speed↔aio-speedd）协商握手**。
- 父任务 PRD AC-3/AC-6 提及"RPC 层复用现有协议头扩展能力宣告"与"服务端默认兼容无协商头存量客户端"，但**未拆出 RPC 层实现子任务**——本任务即补齐该缺口。
- 归档任务 T0246/T0247 为备份传输加密方案/文档优化，与本任务无实现冲突。
- 无重复任务。

## Claim 验证（代码实证）

### 现状：RPC 层无协商，端口即模式

- **客户端** `rpc/rpc-io.cpp:260-277`（connect_server）：`connect()` 后若 `sec_tls_enabled()` **直接** `tls_cert_client_handshake`，随后 `tls_cert_detach_ssl` 还原 raw_fd。无任何协商。
- **服务端** `rpc/rpc-server.cpp:199-212`（StartRPCServiceWoker）：accept 后若 `sec_tls_enabled()` **直接** `tls_cert_server_handshake`。无协商。
- **帧格式** `rpc/rpc-io.cpp:25-122`（rpc_recv/rpc_send）：4 字节网络序长度前缀 + payload（首部 msg_base_t：uiMT+uiLEN）。RPC 消息类型宏见 `rpc/rpc-protocol.h`（MT_EXECUTE_*，最新 MT_KEY_VERIFY=0x00001119）。
- **配置** `libs/rdb-config.c:224`（sec_tls_enabled）：`[security] tls_enable` / env `RPC_TLS_ENABLE`；`sec_tls_ciphersuites`（:251）返回套件串；`tls_cert.c:473` 有 `tls_cert_sm_ciphersuites_configured`（判断是否含 TLS_SM）。
- **结论**：当前 RPC 层在 TLS 开启时所有连接强制 TLS（无明文并存），未实现设计文档 §5"单端口协商"。

### 待实现缺口

设计文档 §5 / §6 RPC 数据流："客户端发起连接 → 读取传输加密开关 → 关闭则走明文存量路径；开启则进行能力协商，目标支持国密套件时同连接升级 TLS；目标不支持时作业失败（ENC-004）"。

## 已确认的决策（用户 P2 对齐）

1. **协商触发**：所有连接先协商再决定（单端口加密/明文并存）。
2. **失败语义**：配置开启但目标不支持国密 → 作业失败、连接关闭，不降级明文（ENC-004）。
3. **协商头形态**：独立专用协商头（magic + 版本 + capability 字段），与 RPC 消息帧独立；TLS 升级后帧格式仍为 rpc_send/recv。
4. **配置来源（每工具独立）**：每个数据链路工具支持自己的配置项控制 TLS 开关与**算法（套件字符串）**，优先级**命令行参数 > 工具配置键 > 全局 [security] 默认**；开关决定是否加密、算法决定套件、**默认算法为国密**；aio-speed/aio-speedd 在本任务实现，其他工具在各自子任务（T0257/T0258/T0259）；连接建立时读取，不重启生效。

## 信息缺口（已通过用户确认闭合）

- 协商头放在 TLS 握手前（明文）——已确认。
- 存量客户端不识别协商头的兼容策略（server 按无能力处理 / 超时降级明文）——需在 PRD 中明确，倾向"server 对无协商头连接视为不要求加密（存量兼容）"。
- 协商超时/半开连接处理——PRD 中定义超时阈值。

## 推荐下一步

进入 Plan 阶段：撰写 PRD（问题、方案、用户故事、测试接缝、验收标准 checkbox），经 P6 终审后进入 Do。