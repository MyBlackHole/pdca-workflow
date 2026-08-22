---
schema: pdca.asset/v1
id: T0353-0823-rpc-net-time-align
phase: check
source_ids: [ac1-time-parse-test, ac2-rdbcomm-grep-clean, ac3-full-build-test, convergence-map]
---

## 上下文

T0352 遗留的 TIME 帧疑点转正：libs/rpc-net.c 内联 AIOH TIME 帧存在 16 字节头越界缺陷且对端已变更为 rpc 项目服务端（MT_GET_TIME 协议）；rdbcomm 的 time 获取协议属定位外冗余。本任务将 rpc_get_time 改为 MT_GET_TIME 协议只对接 rpc 服务端，并从 rdbcomm 全链路移除 time 协议。

## 假设与结果

- **AC-1** rpc_net_time_test：`PASS` — MT_GET_TIME 请求帧构造正确、响应解析正确（含 >2^32 大时间戳字节序往返）、错误响应类型拒绝路径生效。
- **AC-2** rdbcomm time 链路归零：`PASS` — request_time/OP_TIME/OK_TIME/get_time 全仓 grep 为 0；handshake_session_test 其余用例全绿；枚举数值保持原值弃位（NEGOTIATE=2/PLAIN=2/MTLS=3），线上字节零变化。
- **AC-3** xmake build -r 零错误、xmake test **40/40** 全绿（新增 rpc_net_time_test）：`PASS`。

## 分析

- rpc_get_time 新实现与 rpc 项目 msg_base_t/msg_get_time_resp_t 布局逐字段一致（8B 请求 / 20B 响应、be64 时间戳），timed_net_key API 零改动完成对端切换。
- 原 16 字节头缺陷（越界写 2 字节 + 帧长不符）随重写自然消除。
- rdbcomm 六处移除后，旧客户端发 AIOH TIME 帧走 BAD_OPERATION 拒绝路径，符合"移除即不支持"预期。

## 适用边界

- timed_net_key 调用方需保证 host:port 指向 aio-speedd（配置层面，不在代码内）。
- aio-speedd/aio-speed 未做任何改动。

## 下一轮建议

- 无遗留阻塞项；如后续需要校时监控，可在 aio-speedd 侧观察 GET_TIME 访问日志。
