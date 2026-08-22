# rpc-net TIME 改用 MT_GET_TIME 对接 rpc 服务端，rdbcomm 移除 time 协议 — 规格文档

## 问题陈述

- **现状**:
  1. `libs/rpc-net.c` 的 `rpc_get_time` 内联 AIOH TIME 帧客户端存在实锤缺陷：`HS_NET_FIXED_SIZE=16` 与 AIOH 协议 18 字节头不符，且 `hs_put32(wire+14)` 越界 memset 缓冲写 2 字节；该链路（timed_net_key 校时）实际对接目标已变更为 **rpc 项目服务端（aio-speedd）**，而 aio-speedd 使用自有 `MT_GET_TIME`(0x111A) msg 帧协议，不识别 AIOH TIME op。
  2. rdbcomm 项目仍保留完整 time 获取协议：client 端 `rdb_hs_request_time`/`rdbcomm_get_time`、服务端 first_stage 的 `RDB_HS_OP_TIME` 分支、main 工具 "time" 子命令——与"rdbcomm 不做校时服务"的定位冲突。
- **目标**: libs/rpc-net.c 的 time 客户端改用 MT_GET_TIME 协议只对接 rpc 服务端；rdbcomm 全链路移除 time 获取协议；timed_net_key 对外 API 不变。
- **差距**: rpc-net.c 重写 + rdbcomm 六处清理（io.h/io.c/client.c/client.h/main/测试）。

## 解决方案

1. **libs/rpc-net.c 重写 `rpc_get_time(fd, &timestamp)`** 为 MT_GET_TIME 协议：
   - 请求：8 字节 `{uiMT=htonl(MT_GET_TIME), uiLEN=0}`；
   - 响应：20 字节 `msg_get_time_resp_t` 布局 `{uiMT=MT_GET_TIME_RESP, uiLEN, uiResult, timestamp(uint64 网络序)}`；
   - 校验 uiMT == MT_GET_TIME_RESP 后 be64toh 取 timestamp；
   - 局部宏/常量随实现内联（不再引用 AIOH 魔数）；`rpc_server_connect` 保持不变。
2. **timed_net_key 零改动**：API 签名不变，仅通信对端语义变化为 aio-speedd。
3. **rdbcomm 移除 time 获取协议**：
   - io.h/io.c：删 `RDB_HS_OP_TIME`、`RDB_HS_OK_TIME` 枚举值、`rdb_hs_request_time` 及实现、first_stage 的 OP_TIME 分支；negotiate_frame 结果合法区间收窄为 OK_PLAIN..OK_MTLS；
   - client.c/client.h：删 `rdbcomm_get_time`；
   - rdbcomm-main.c：删工具 "time" 子命令及其参数分支；
   - tests/handshake_session_test.c：删 TIME 用例（其余保留）。
4. **兼容性说明**：移除后旧客户端向 rdbcommd 发 AIOH TIME 帧将走 BAD_OPERATION 拒绝路径（预期行为）。

## Seam 分析

### 声明的测试接缝

- seam: libs/xmake.lua -> timed_net_key
- seam: rdbcomm/tests/handshake_session_test.c -> io.h
- seam: rdbcomm/tests/handshake_session_test.c -> io.h

### 验收可测性

- MT_GET_TIME 新实现以链接级往返验证（构造本地伪服务端回固定 timestamp，断言解析正确）。
- rdbcomm 移除以 grep 断言（request_time/OP_TIME/get_time 归零）+ 测试套件全绿。

## 用户故事

1. 作为 timed_net_key 使用者，校时请求发往 rpc 服务端即可获得正确时间戳，不再依赖 rdbcomm。
2. 作为 rdbcomm 维护者，项目内无冗余 time 协议代码，握手首阶段只处理 NEGOTIATE。

## 实现决策

- **切片 A**：libs/rpc-net.c 重写 rpc_get_time（MT_GET_TIME 协议），同步修正原 16 字节越界缺陷。
- **切片 B**：rdbcomm 移除 time 全链路（六处）。
- **技术澄清**:
  - MT_GET_TIME 帧为纯 C 可手工构造的字节布局（uiMT/uiLEN 大端），无需引入 C++ 头。
  - 响应 uiResult 字段不做强校验（服务端未赋值），只校验 uiMT 与长度。
  - 移动而非新增抽象：rpc-net.c 内联实现，不新建文件。

## 测试决策

- 新增链接级单测覆盖 rpc_get_time 解析（伪服务端回帧）；rdbcomm 以现有套件回归 + grep 归零。

## 验收标准

- [ ] AC-1: 新增 rpc_get_time 链接级测试 PASS（MT_GET_TIME 请求构造与响应解析正确，含错误响应拒绝路径）。
- [ ] AC-2: rdbcomm 全仓 grep "request_time|OP_TIME|OK_TIME|rdbcomm_get_time" 归零；handshake_session_test 其余用例全绿。
- [ ] AC-3: xmake build -r 全量成功无新增警告；xmake test 相关套件（libs/rdbcomm/rpc）全绿。

## 范围外

- 不改 aio-speedd/aio-speed 服务端与客户端（协议已存在且稳定）。
- 不改 timed_net_key API 与调用方端口配置。
- 不处理 AIOH TIME op 的历史兼容（移除即不支持）。

## 备注

- 前置：T0352 conclusion 已标记 HS_NET_FIXED_SIZE=16 越界疑点，本任务一并消除。
