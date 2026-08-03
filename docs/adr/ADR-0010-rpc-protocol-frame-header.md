# ADR-0010: rpc 协议演进 — 16 字节帧头（对齐 tRPC）

- 日期: 2026-08-03
- 状态: 已确认（含流式扩展 + 心跳/错误码）

## 背景

rpc wire 层无帧头（仅 4 字节 mlen + msg_base），无魔数/版本/长度上限，无法安全演进协议；大帧整帧缓冲（64MB）内存峰值高。

## 决策

wire 层增加 16 字节固定帧头（对齐 tRPC 设计）：

```
0-3   magic       'FSBC' = 0x46534243
4     version     = 1
5     type        0=请求 1=响应 2=流数据(STREAM) 3=Ping 4=Pong（心跳）
6-7   flags       bit0=COMPRESSED bit1=ENCRYPTED bit2=END（帧级）
8-11  total_len   帧总长含帧头
12-15 msg_id      请求 ID（预留多路复用）
```

收包顺序强制：读帧头 → magic 校验 → version 校验 → total_len 上限（8MB）校验 → 分配。

流式扩展（对齐 gRPC streaming + PBS 4MB chunk）：大文件传输用 type=2 流帧序列 INIT→N×DATA(4MB)→END，块级压缩/加密/校验，块缓冲池化，内存峰值 O(4MB)。INIT 帧带 timeout_ms 请求级 deadline（对齐 Seastar timeout propagation）。

心跳（对齐 uRPC Ping/Pong）：type=3/4，空闲连接按 keepalive_interval 周期 Ping，无 Pong 响应判定死连接断开，补充内核 SO_KEEPALIVE（2h）检测盲区。

错误码体系（对齐 tRPC 错误模型）：标准化枚举 `RPC_ERR_OK/RPC_ERR_PROTO_VERSION/RPC_ERR_FRAME_TOO_LARGE/RPC_ERR_BAD_MAGIC/RPC_ERR_TIMEOUT/RPC_ERR_IO/RPC_ERR_PEER_CLOSED`，响应/END 帧带可读错误消息字符串。

## 权衡

- 备选：8 字节最小帧头 —— 放弃（无 msg_id 扩展位）
- 备选：不加魔数仅加 version —— 放弃（失去协议识别能力）
- 备选：引入 protobuf/capnproto —— 放弃（单语言、无跨语言需求、消息体多为文件数据）
- 备选：纯 C++ 化序列化 —— 放弃（项目 116 .c + 112 .cpp 混合工程；uRPC 证明 C 序列化可行，msg_base 本就是 C struct；避免 extern "C" 桥接；分层：序列化层 C / 传输调度层 C++）
- 备选：应用层心跳用连接级超时替代 —— 放弃（读超时无法发现对端挂死但连接未关的场景）
- 备选：信用流控（credit/window）—— 放弃（单连接单流，TCP 窗口即背压；多路复用启用后再引入）
- header 永不加密（uRPC 实践），仅 payload 加解密

## 影响

- 两端同步升级；版本不匹配返回 `RPC_ERR_PROTO_VERSION` 并断开
- msg_base（uiMT/uiLEN）保持不动（业务层 159 处依赖 uiLEN）
