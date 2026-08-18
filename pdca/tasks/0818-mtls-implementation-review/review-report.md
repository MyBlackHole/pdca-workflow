# mTLS 实现审查报告

审查基点：`df6b6145^..HEAD`，包含统一握手实现及 `437cdd31` RPC 应用测试握手修复。工作树审查时无未提交代码改动。

## 结论摘要

结论：部分满足，不建议以当前状态宣称“RPC 全面支持 mTLS”。统一首阶段协议、时间功能、rdbcomm 主数据面和部分 RPC session 数据面已经接入；但 RPC 仍存在大量 fd-only 业务路径，且连接函数在 mTLS 协商成功后直接失败，导致这些路径无法使用 mTLS。另有服务端 SSL 清理、握手响应校验和超时语义缺口。

## 标准轴

### P1 — RPC fd-only 连接 API 与 mTLS 数据面不闭合

- 证据：`rpc/rpc-io.cpp:346-455` 的 `connect_server/connect_server2` 调用首阶段协商；`rpc_connect_first_stage` 在结果为 `RPC_HS_OK_MTLS` 时记录错误并返回失败。
- 影响：`rpc/rpc.cpp:1327` 等调用这些接口的业务函数，在服务端启用 mTLS 时连接直接失败；即便连接成功的明文路径，`rpc_send/rpc_recv` 包装器仍固定初始化 plain I/O（`rpc/rpc-io.cpp:327-339`）。
- 建议：统一 RPC 连接返回对象为带 `rpc_io_t` 的 session，或把所有可达业务函数迁移到 session I/O；在迁移完成前，至少建立调用图并禁止 mTLS 配置下进入 fd-only API。删除或废弃 `tls_cert_detach_ssl`，避免重新引入裸 fd。

### P1 — RPC 服务端 SSL 对象在普通连接退出路径未清理

- 证据：`rpc/rpc-server.cpp:231-235` 将 SSL 放入 `woker_info->io`，但 `:436-445` 只 `shutdown/close/delete`，没有 `rpc_hs_session_cleanup` 或等价的 `SSL_free`。
- 影响：每个 mTLS RPC 连接退出都可能泄漏 SSL 对象及其内部资源；长时间运行的服务会累积。
- 建议：将 `rpc_hs_session_cleanup(&woker_info->io)` 放入唯一退出清理路径，并明确 fd 与 SSL 的所有权，避免 `shutdown/close` 与 SSL cleanup 双重关闭。

### P2 — I/O 错误处理没有区分 SSL 错误

- 证据：`rpc/rpc-io.cpp:167-232`、`:265-323` 统一按 `errno/EAGAIN` 处理 `io->read/io->write` 结果；TLS 回调实际调用 `SSL_read/SSL_write`。
- 影响：TLS `WANT_READ/WANT_WRITE`, protocol error 和真实 socket error 可能被记录为相同错误，超时/重试/诊断不准确。
- 建议：按 transport 类型调用 `SSL_get_error`，为 `SSL_ERROR_WANT_READ/WRITE/SYSCALL/SSL` 建立统一映射；错误日志记录握手阶段、算法和具体 TLS reason。

### P2 — 宏替换隐藏真实传输对象

- 证据：`rpc/rpc-server.cpp:449-450`、`:984-985` 以宏忽略传入 fd，改用词法作用域中的 `conn->io`。
- 影响：调用者看到的是 fd API，实际是 session API；后续新增代码容易在错误作用域或错误连接上发送，审查和静态分析也难以发现裸 fd 绕过。
- 建议：把业务函数参数和发送/接收接口显式改为 `rpc_hs_session_t/rpc_io_t*`，删除宏和兼容性伪装。

## 规范轴

### 已满足或基本满足

1. 首阶段时间场景：RPC 与 rdbcomm 服务端收到 `RPC_HS_OP_TIME` 后返回时间并关闭连接；客户端分别由 `rpc_get_time` 和 `rdbcomm_get_time` 请求并关闭连接。
2. 首阶段未知 operation：两端均返回 `RPC_HS_ERR_BAD_OPERATION`；坏帧可返回 `RPC_HS_ERR_FRAME`。
3. 服务端强制 mTLS：`rpc_hs_decide` 在服务端要求 mTLS 且客户端未请求/算法不一致时拒绝；未发现静默降级到明文的路径。
4. mTLS 后密文 I/O：rdbcomm 及 RPC session 路径通过握手结构体中的 `read/write` 指针调用 `SSL_read/SSL_write`；未再使用 `tls_cert_detach_ssl`。
5. 客户端多证书提示：服务端响应携带 `sec_tls_ca_cn()`，客户端按该 `ca_cn` 调用 `tls_cert_client_handshake_for_cn`；证书目录分隔符也有安全校验。
6. 既有参数：客户端使用既有 `RPC_TLS_ENABLE` 与 `RPC_TLS_CIPHERSUITES`，未发现此前讨论中新增的 mTLS 开关/算法参数。

### 部分满足或无法证明

#### P1 — RPC 全业务面并未满足 mTLS

规范要求“RPC 开启加密后进入密文数据流”。当前只有 `connect_server_session` 和部分 `rpc-client/rpc-conn` session 路径能保留 SSL；`rpc.cpp` 中大量业务调用仍使用 fd-only 接口。现有 `download_file`、`execute_command` 测试只验证了明文首阶段后的应用帧，不能证明 mTLS 应用帧。

#### P1 — 握手协议响应校验不完整

`libs/rpc-handshake.c:270-281` 的 `rpc_hs_client_negotiate` 只检查 response flag 和 result 范围，没有要求 `resp.operation == RPC_HS_OP_NEGOTIATE`；因此错误 operation 的成功结果可能被当作协商成功。服务端也应明确拒绝带 response flag 的请求及不符合 operation 的字段组合。

#### P1 — 首阶段错误码没有精确传播

服务端对 `rpc_hs_recv` 的 magic/version/frame 解析失败统一发送 `RPC_HS_ERR_FRAME`（例如 `rpc-server.cpp:210-214`、`rdbcomm/server.c:438-443`），无法区分坏 magic、版本不匹配和长度错误。基线要求协议版本不匹配、组件不支持等失败可诊断，当前只能部分满足。

#### P1 — 握手及获取时间缺少客户端超时边界

`rpc_hs_session` 的 `io_full`（`libs/rpc-handshake.c:187-203`）是阻塞循环；`rpc_get_time`/`rdbcomm_get_time` 建立连接后没有设置明确的发送/接收超时。对端只发半帧或不响应时可能长期阻塞。

#### P2 — 算法类型被二值化

RPC/rdbcomm 通过 `strstr(sec_tls_ciphersuites(), "SM")` 在 `RPC_HS_ALG_SM` 与 `RPC_HS_ALG_CLASSIC` 间选择（如 `rpc-server.cpp:197-199`、`rdbcomm/client.c:178-180`）。这能覆盖当前 SM/classic 两类，但不能表达服务端配置的具体算法类型或多个套件的最终选择；日志也未记录实际协商套件。

#### P2 — 失败路径 SSL 所有权不统一

`rdbcomm/client.c:187-249` 完成 TLS 后，后续构造初始化消息或状态失败时直接 `close(sockfd)`；如果调用方未立即调用 `rdbcomm_free`，`hs.ssl` 没有 cleanup。应由 `rdbcomm_connect` 自己完成失败回收。

## 基线文档映射

对 `/home/black/Public/aio/F/139/备份传输存储加密/备份复制传输加密.md` 的 RPC/rdbcomm 相关条款：

- 单端口首阶段协商、同连接升级、开启即失败不降级：协议骨架已实现，但 RPC fd-only 路径使全量业务不满足。
- 加密开关和既有套件配置：既有参数已接入；动态配置“新连接生效、存量连接不受影响”未通过本次代码/测试充分证明。
- 密文传输：rdbcomm 主路径和 RPC session 路径满足；RPC 全业务路径无法证明且存在明确失败路径。
- 失败原因和可观测性：有部分错误枚举与 TLS 日志，但错误细分、实际套件/后端/连接加密状态指标未完整实现。
- 证书缺失、信任链、SM2/SM4：tls_cert 单测覆盖了常规 mTLS 和 SM2 套件链加载；本次未证明 RPC/rdbcomm 首阶段到真实 SM2 密文业务帧的端到端链路。

范围外差距：基线文档中的 SBT（dmsbtex/libobk/dm-ftp/FileTransferAgent）、UI/作业层开关、完整 GMSSL 双后端、存储加密和性能/容量验收不属于本次 RPC/rdbcomm 代码审查，不能据此宣称全量基线满足。

## 建议优先级

1. P0/P1：先统一 RPC 业务连接对象和 I/O，消除 fd-only mTLS 失败/裸 fd 路径；补真实 RPC mTLS 应用帧测试。
2. P1：补 RPC 服务端和客户端所有 SSL 失败/退出路径的唯一 cleanup；增加握手、时间请求的读写超时。
3. P1：严格校验 operation/version/response/result 的组合，并逐项返回明确错误码。
4. P2：将算法配置解析与“实际 TLS cipher”分离，记录最终协商套件、证书 `ca_cn` 摘要和加密状态。
5. P2：删除 fd 参数宏和废弃 detach 接口，减少两套 I/O 抽象并存造成的回归风险。

## 验证结果

- `xmake build -y`: PASS。
- `xmake run rpc_handshake_test`: PASS。
- `xmake run tls_cert_test`: 21 passed, 0 failed；包含常规 mTLS 与 SM2 mTLS 数据收发。
- `xmake run rdb_config_test`: 11 passed, 0 failed。
- `xmake run download_file`: 3 cases PASS。
- `xmake run execute_command`: PASS。
- `git diff --check df6b6145^..HEAD`: PASS。
- 未发现可直接运行的真实 RPC/rdbcomm 首阶段到 mTLS 应用业务帧回归目标；该覆盖缺口仍需后续任务补齐。
