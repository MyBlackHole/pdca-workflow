# PRD — RPC 自实现握手：移除 rpc-handshake，明文默认，mTLS 按需握手

## 问题陈述

- **现状**: RPC 层（aio-speed↔aio-speedd）依赖外部库 `rpc-handshake`（`libs/rpc-handshake.c`）处理连接前握手。该库实现了完整的协商协议（AIOH magic + 能力位图 + 算法协商 + 时间同步），但引入了不必要的复杂度：协商头格式、能力位图、ENC-004 语义、多算法协商等。
- **目标**: RPC 层自己实现握手逻辑，移除对 `rpc-handshake` 的依赖。设计简化为：默认明文通信，服务端配置 mTLS 后才进行 TLS 握手；服务端未配置 mTLS 时同时支持明文与加密连接。
- **差距**: 当前 RPC 连接路径（`rpc-server.cpp:216` `rpc_hs_server_accept`、`rpc-io.cpp:139` `rpc_hs_client_negotiate_config`）直接调用 rpc-handshake API。移除后需在 RPC 层内联实现等效功能。

## 设计决策

### 核心行为

| 服务端 mTLS | 客户端 mTLS | 行为 |
|------------|------------|------|
| 关闭 | 关闭 | 明文通信 |
| 关闭 | 开启 | 客户端尝试 TLS 握手，服务端接受（明文+加密并存） |
| 开启 | 关闭 | 服务端拒绝明文连接 |
| 开启 | 开启 | TLS 握手成功，加密通信 |

### 协议设计

使用 RPC 原有帧格式（4字节长度前缀 + `msg_base_t`），通过 `uiMT` 字段区分握手包和数据包：

- **HANDSHAKE 消息** (`uiMT = MT_HANDSHAKE`): 客户端发起握手，携带 mTLS 意愿标志。服务端根据自身配置决定是否接受 TLS 握手。
- **TIME 消息** (`uiMT = MT_TIME`): 客户端请求时间戳，服务端响应。明文/TLS 均可。
- **RPC 数据消息** (`uiMT = 其他`): 正常 RPC 数据传输。

```
// MT 常量
#define MT_HANDSHAKE 0x0000111B           // 握手请求/响应
#define MT_HANDSHAKE_RESP ((NORMAL_RESP) | MT_HANDSHAKE)

// 握手消息类型（继承 msg_base_t）
typedef struct msg_handshake__ : public msg_base__ {
    uint16_t flags;       // bit0=MTLS_REQUEST
    uint16_t algorithm;   // DEFAULT=0, SM4=1, AES=2
    char ca_cn[RPC_MAX_NAME + 1];  // CA Common Name（服务端响应时填充）
} msg_handshake_t;

typedef struct msg_handshake_resp__ : public msg_base_resp__ {
    uint16_t result;      // OK_PLAIN=2, OK_MTLS=3, ERR_MTLS_REQUIRED=0x8004
    uint16_t algorithm;
    char ca_cn[RPC_MAX_NAME + 1];
} msg_handshake_resp_t;

// 帧格式（RPC 标准帧）:
  [0..3]   长度前缀 htonl(len)
  [4..7]   uiMT = MT_HANDSHAKE / MT_HANDSHAKE_RESP
  [8..11]  uiLEN = sizeof(msg_handshake_t) / sizeof(msg_handshake_resp_t)
  [12..]   msg_handshake_t / msg_handshake_resp_t（需 hton/ntoh）
```

### 服务端握手逻辑

```
accept(fd)
  -> 读取 RPC 帧（4字节长度前缀 + msg_base_t）
  -> 解析 uiMT 字段
  -> 如果 uiMT == MT_HANDSHAKE:
       -> 解析握手消息（flags, algorithm, ca_cn）
       -> 如果服务端 mTLS 关闭:
            -> 如果客户端 flags 含 MTLS_REQUEST -> 响应 MT_HANDSHAKE_RESP(OK_MTLS, ca_cn)
               → 执行 TLS 握手（tls_cert_server_handshake）
            -> 否则 -> 响应 MT_HANDSHAKE_RESP(OK_PLAIN)
       -> 如果服务端 mTLS 开启:
            -> 如果客户端 flags 含 MTLS_REQUEST -> 响应 MT_HANDSHAKE_RESP(OK_MTLS, ca_cn)
               → 执行 TLS 握手
            -> 否则 -> 响应 MT_HANDSHAKE_RESP(ERR_MTLS_REQUIRED)，关闭连接
   -> 如果 uiMT 是其他值（RPC 数据 / MT_GET_TIME）:
        -> 如果服务端 mTLS 开启且 uiMT != MT_GET_TIME -> 响应 ERR_MTLS_REQUIRED，关闭连接
        -> 否则 -> 按正常 RPC 数据处理（进入 while 循环，MT_GET_TIME 豁免）
```

### 客户端握手逻辑（连接后按状态）

```
connect_server_session(ip, port):
  fd = socket + connect
  rpc_io_init_plain(io, fd)
  if mtls_enabled:
      MT_HANDSHAKE(flags=MTLS_REQUEST, algorithm) → rpc_send
      MT_HANDSHAKE_RESP ← rpc_recv
      if result==OK_MTLS → tls_cert_client_handshake → rpc_io_init_tls
      if result==OK_PLAIN → 保持明文
      if result==ERR_MTLS_REQUIRED → 失败
  else:
      保持明文，不发 HANDSHAKE

connect_server / rpc_get_time 等 fd-only 路径：仅建连，不握手（明文）
```

### TIME 操作

复用 RPC 已有 `MT_GET_TIME(0x111A)` 走正常 RPC 数据通路（while 循环内处理），不参与握手阶段逻辑。

### 配置来源

复用现有配置（`rpc-config.h`）：
- `mtls_enabled`: mTLS 开关
- `tls_algorithm`: TLS 算法（ed25519/sm2）
- `ca_cert`, `server_cert`, `server_key`: 服务端证书
- `client_cert`, `client_key`: 客户端证书
- `ca_cn`: CA Common Name

### 会话模型

保持现有 `rpc_hs_session_t` 结构（或等效的 `rpc_io_t`）：
- `fd`: 底层 socket
- `ssl`: OpenSSL SSL 对象（TLS 模式下非 NULL）
- `tssl`: TLS_SSL 封装
- `read`/`write`: 函数指针（plain 或 TLS）

### 范围

- **包含**: RPC 层（`rpc-protocol.h` 新增 `MT_HANDSHAKE`、`rpc-server.cpp`、`rpc-io.cpp`）自实现握手逻辑
- **涉及文件**: `rpc/rpc-protocol.h`（新增 MT 定义+消息结构）、`rpc/rpc-protocol.cpp`（编解码）、`rpc/rpc-server.cpp`（服务端握手）、`rpc/rpc-io.cpp`（客户端握手 + rpc-io.h 去依赖）
- **构建**: `rpc/xmake.lua` 移除 `rpc-handshake.c` 依赖，`libs/rpc-handshake.c` 文件保留供 rdbcomm/dmsbtex 使用
- **不包含**: rdbcomm、dmsbtex 等其他子系统的握手改造；tls_cert 库变更；配置项变更

## Seam 分析

### 声明的测试接缝

- seam: rpc/tests/rpc_own_handshake_test.cpp -> rpc/rpc-server.cpp（服务端握手逻辑）
- seam: rpc/tests/rpc_own_handshake_test.cpp -> rpc/rpc-io.cpp（客户端握手逻辑）

## 用户故事

1. 作为运维，我希望 RPC 默认明文通信，配置 mTLS 后自动切换为加密，以便平滑升级。
2. 作为 DBA，我希望服务端配置 mTLS 后拒绝明文连接，以便满足安全合规要求。
3. 作为开发者，我希望移除 rpc-handshake 外部依赖，以便简化构建和维护。

## 验收标准

- [ ] AC-1: RPC 连接建立路径不再调用 `rpc_hs_*` 系列函数，`rpc/xmake.lua` 移除 `rpc-handshake.c` 依赖（保留文件供 rdbcomm/dmsbtex）
- [ ] AC-2: 服务端 mTLS 关闭时，客户端直接发送 RPC 数据（无 HANDSHAKE 包）→ 正常处理
- [ ] AC-3: 服务端 mTLS 关闭时，客户端发送 HANDSHAKE 包（flags=MTLS_REQUEST）→ 服务端响应 OK_MTLS（含 ca_cn）→ 客户端执行 TLS 握手成功
- [ ] AC-4: 服务端 mTLS 开启时，收到 HANDSHAKE 包（MTLS_REQUEST）→ 服务端响应 OK_MTLS（含 ca_cn）→ TLS 握手成功
- [ ] AC-5: 服务端 mTLS 开启时，收到 RPC 数据包（非 HANDSHAKE 且非 MT_GET_TIME）→ 服务端返回 MT_HANDSHAKE_RESP(ERR_MTLS_REQUIRED) → 关闭连接；MT_GET_TIME 豁免
- [ ] AC-6: TIME 消息（MT_GET_TIME）在明文和 TLS 连接下均正常工作（业务循环内，mTLS 开启时豁免）
- [ ] AC-7: 现有 RPC 数据传输（rpc_send/rpc_recv）在明文和 TLS 连接下行为不变
- [ ] AC-8: 构建无警告（-Werror），38/38 现有测试通过
- [ ] AC-9: 新增 `rpc/tests/rpc_own_handshake_test.cpp` 覆盖握手四象限

## 范围外

- rdbcomm 握手改造
- dmsbtex/libobk 握手改造
- tls_cert 库变更
- 新增配置项
- 存量旧 rpc-handshake 客户端兼容

## 备注

- 替代已归档任务 T0260（0817-rpc-handshake-negotiation）
- 使用 RPC 原有帧格式（4字节长度前缀 + msg_base_t），通过 `MT_HANDSHAKE(0x111B)` 区分握手/数据包
- 不兼容旧 rpc-handshake 客户端（clean break）
- `libs/rpc-handshake.c` 文件保留，其他工具迁移完再删除
