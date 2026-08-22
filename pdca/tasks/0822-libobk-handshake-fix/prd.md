# 跟进：修复 libobk mTLS 握手栈溢出与帧长度必败（C1/C2）并补往返测试

## 问题陈述

父任务 T0355 一致性审查发现 libobk mTLS 握手路径两项 CRITICAL 缺陷（数值经编译验证 sizeof(activeioHeader)=30）：

- **C1 栈溢出**：`sbt_session_client_init` 中 `char resp[4+201]`（205 字节）被 `_recv(io, resp, sizeof(activeioHeader)+sizeof(resp), NULL)` 读入 235 字节 → 溢出 30 字节。
- **C2 必败+越界读**：客户端校验 body 长度 `sizeof(resp)-sizeof(activeioHeader)`=175，服务端发送 h.bytes=`4+201`=205 → 校验必败，mTLS 升级永不成功；且服务端从 `resp[204]` 发送 205 字节越界读 1 字节。
- **测试缺口**：libobk/test/session_test.c 仅覆盖配置解析与会话 IO 原语，双端契约漂移无法发现。
- 顺带（M4）：`result ? obk_hs_algorithm_name(halg) : ctx->tls_algorithm_name` 死分支。

## 方案

1. **长度常量单点化**：protocol.h 新增 `OBK_HS_RESP_BODY_SIZE (4 + OBK_HS_MAX_NAME)`（=204，body={result u16, algorithm u16, ca_cn[200]}），客户端校验与服务端发送共用。
2. **客户端缓冲区修复**：接收缓冲区扩为 `sizeof(activeioHeader) + OBK_HS_RESP_BODY_SIZE`，`_recv` expect 改为 `sizeof(resp)`；校验改为 `ph->bytes == OBK_HS_RESP_BODY_SIZE`；ca_cn 提取用 `OBK_HS_MAX_NAME`。
3. **服务端对齐**：resp 数组与 hs_send_frame 长度均引用宏，消除越界读。
4. **测试导出**：`sbt_session_client_init`（libobk.c）与 `sbt_session_server_handshake`（oracleCmdTbl.c）去 static，在 include/ 头声明，供测试链接（xmake libobk_session_test 已同时编译两源文件）。
5. **往返测试**：session_test.c 新增 socketpair 级真实 TLS 升级往返用例——服务端线程经 sbt_session_server_prepare + sbt_session_server_handshake，客户端跑 sbt_session_client_init，断言双方会话读写函数切换为 TLS 实现；升级后互发一帧验证走 SSL 通道。
6. **M2 最小诊断日志**（范围待确认）：客户端握手各 fail 分支补一条分类 ErrorLog。
7. **M4**：删除死分支三元表达式。

## 用户故事

- 作为维护者，我能在开启 SBT_MTLS_ENABLE=1 后真实完成 libobk↔FileTransferAgent 的 mTLS 握手。
- 作为维护者，我能通过往返集成测试防止未来双端契约再次漂移。

## 实现/测试决策

- bugfix 场景，TDD：先写失败的往返测试（当前代码下必失败——C2 校验拦截），再最小修复使其通过。
- 证书复用 `libs/tests/certs/` 现有 CA/host 证书（TEST_CERT_DIR 宏已由 xmake 注入）。
- ASan 构建验证内存安全（xmake add_cflags -fsanitize=address 临时构建或独立 target）。

## Seam 分析

### 声明的测试接缝
- seam: libobk/test/session_test.c -> libobk/lib/sbt/libobk.c（sbt_session_client_init）
- seam: libobk/test/session_test.c -> libobk/lib/logic/oracleCmdTbl.c（sbt_session_server_handshake / sbt_session_server_prepare）

## 范围外

- dmsbtex 同域代码（弹性范围校验无此缺陷，保持任务聚焦）。
- T0355 H1–H3/M1/M3 等语义收敛项（另行任务）。
- 证书生成与管理本身。

## 备注

- 相关知识：knowledge/tls/handshake-dup-impl-length-contract.md（本任务的规则来源）。
- rdbcomm/tests/handshake_session_test.c 的 socketpair 握手测试模式可作参照。

## 验收标准

- [ ] AC-1: 运行 `xmake build libobk_session_test && xmake test` 得到构建成功、既有用例全绿且新增 mTLS 往返用例通过。
- [ ] AC-2: 运行新增往返用例得到双方会话读写函数指针均切换为 TLS 实现的断言通过（升级成功路径真实可达）。
- [ ] AC-3: 运行 `grep -n "4 + 201\|4+201\|+ 205\|== 175" libobk/lib/sbt/libobk.c libobk/lib/logic/oracleCmdTbl.c` 得到 0 处命中（帧长度仅由 OBK_HS_RESP_BODY_SIZE 单点定义）。
- [ ] AC-4: 运行 ASan 构建的 libobk_session_test 往返用例得到无内存错误报告（栈溢出修复验证）。
