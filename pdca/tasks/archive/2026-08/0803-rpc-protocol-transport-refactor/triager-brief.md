# Triage Brief: rpc 协议层与传输层重构

## 分类

- **category**: enhancement
- **scenario_type**: development（重构 / 优化）

## 验证结果

已通过代码验证的事实（不依赖用户陈述）：

1. **协议无魔数/版本号**：rpc-protocol.h 帧头仅 `uiMT + uiLEN` 4+4 字节，无协议识别/版本字段，解析错误时无检测手段。
2. **收包无长度上限**：`rpc/rpc-msg.c:76` `rpc_recv_msg` 从网络读取 4 字节 msg_len 后直接 `buf_reserve(msg, msg_len)`，无任何上限校验 —— 恶意/损坏对端可触发超大内存分配（安全缺陷）。
3. **部分读写未处理**：`rpc-msg.c:14` `readn` 在 EAGAIN 时 break 返回部分读取；`rpc-msg.c:53` `rpc_send_msg` 用 writev 单次调用，大消息/非阻塞场景可部分写入导致丢数据。
4. **序列化样板重复**：rpc-protocol.cpp 941 行中绝大多数为每消息 4 个 hton/ntoh 函数的重复样板；`rpc_conn` 相关 `htonll/ntohll` 为手写 64 位转换。
5. **平台不一致**：`msg_nc_extend_resp_t.rate` 为 `unsigned long`（rpc-protocol.h:421），32/64 位平台序列化长度不一致。
6. **命名混乱**：`mmsg_ioctl_fsbackup_resp__`（多一个 m，rpc-protocol.h:461）、`bolck_num`（拼写错误，rpc-protocol.h:319）、`decr`（rpc-protocol.h:439/457）。
7. **C/C++ 混编**：rpc-protocol.h 在 `extern "C"` 内使用 C++ 继承（`msg_base_resp__ : public msg_base__`）；rpc-msg.c/rpc-metadata.c 为 C 但所有调用方是 .cpp。
8. **阻塞重试宏**：`RPC_CONN_RETRY`（rpc-conn.h:26）while + sleep(1)，无超时上限。
9. **协议两端同仓库**：MT_EXECUTE_* 消息类型仅被本仓库 .cpp 引用，无外部实现（rpc-keygen 不依赖协议层），可安全同步演进。

## 信息缺口

- 帧头魔数/版本具体布局（设计决策，需用户确认或 ADR）
- 长度上限取值（建议基于现有 MSG_RESP_BUFF_LEN=64MB 推导）

## 查重结果

- `$PDCA_HOME/pdca/tasks/`（active + archive）与 `$PDCA_HOME/knowledge/` 无 rpc 相关历史任务，无重复。

## 推荐下一步

进入 Plan 阶段 P2 Grill：确认帧头格式与长度上限设计决策，然后合成完整 PRD。
