# 详细设计：显式参数驱动的 mTLS

## 1. 设计边界

本任务只处理当前版本的显式 mTLS 协议和证书布局，不兼容历史证书目录、旧算法别名、fd-only TLS 调用和隐式证书选择。RPC 一阶段协议不变，`TIME` 与 `NEGOTIATE` 继续是两个并列操作。

## 2. 一阶段状态机

### TIME 分支

```text
client connect
  → plain session
  → send TIME
  → receive TIME response
  → close session/fd
```

TIME 不进入 NEGOTIATE，也不触发证书选择和 TLS 升级；它保留现有时间同步语义。TIME 的客户端 API 必须明确自己拥有并关闭连接，避免 fd 所有权歧义。

### NEGOTIATE 分支

```text
client/server connect
  → plain session
  → NEGOTIATE(client flags, preferred algorithm)
  → server selects from supported modes
  → NEGOTIATE response(result, selected algorithm, ca_cn)
  → result=PLAIN: keep plain session
  → result=MTLS: load explicit certificate chain and upgrade same session
  → business frames through session read/write
```

服务端收到 TIME 时只返回 TIME 响应；收到 NEGOTIATE 时才执行算法、mTLS 要求和证书链处理。两条分支不得互相隐式转换。

## 3. 配置模型

配置层解析为内部结构，不让 TLS 层读取环境变量名。服务端配置是可并存的 profile 列表，客户端配置是本次连接的 profile 偏好：

```c
typedef struct {
    uint16_t algorithm;
    char ca_cn[RPC_HS_MAX_NAME + 1];
    char ca_cert[PATH_MAX];
    char cert[PATH_MAX];
    char key[PATH_MAX];
} tls_profile_t;

typedef struct {
    int allow_plain;
    tls_profile_t profiles[2];
    size_t profile_count;
    uint16_t preferred_algorithm;
} tls_config_t;
```

每个 profile 是一个独立的“算法 + ca_cn + 证书链”组合：

```c
TLS_SM4_GCM_SM3       → SM2 ca_cn/ca.crt/host.crt/host.key
TLS_AES_256_GCM_SHA384 → 普通 ca_cn/ca.crt/host.crt/host.key
```

推荐默认服务端同时配置：

```text
allow_plain = true
profile[SM4] = { algorithm, ca_cn, ca_cert, cert, key }
profile[AES] = { algorithm, ca_cn, ca_cert, cert, key }
```

服务端启动时校验并加载/准备所有 profile，但每条连接只绑定一个选中的 profile；profile 之间不得共享可变 SSL_CTX 或证书选择状态。客户端每次连接只发送一个偏好算法或明确请求 PLAIN。服务端按 profile 查找，并在响应中返回实际选中的算法：

| 客户端请求 | 服务端能力 | 结果 |
|---|---|---|
| PLAIN | 含 PLAIN | PLAIN |
| SM4 | 含 SM4 | SM4 mTLS |
| AES | 含 AES | AES mTLS |
| SM4/AES | 不含对应算法 | 算法不匹配 |
| mTLS | 只含 PLAIN | 拒绝，不降级 |

现有 `algorithm` 字段可继续承载客户端偏好和服务端选中算法，不增加业务帧；证书 profile 的 ca_cn 继续通过响应返回。

来源优先级固定为：

```text
CLI > 模块环境变量 > 模块配置节 > [security] 全局配置 > 默认值
```

解析规则：

- profile 算法只接受 `TLS_SM4_GCM_SM3`、`TLS_AES_256_GCM_SHA384`，同一算法不得重复。
- 每个 profile 必须有独立、合法的 ca_cn 和证书路径；缺失或路径越界启动失败。
- 客户端偏好只接受 `plain` 或当前 profile 中存在的完整算法名。
- `ca_cn` 只接受单级目录名，拒绝空值、`.`、`..`、`/`、`\\` 和超长值。
- 配置解析完成后，握手和 TLS 层不再重新解析环境变量。

## 4. 证书加载模型

证书路径由显式 `ca_cn` 确定，不扫描目录、不遍历 CA 列表、不猜测证书：

```text
<cert_root>/<ca_cn>/ca.crt
<cert_root>/<ca_cn>/host.crt
<cert_root>/<ca_cn>/host.key
```

SM2 使用同一确定目录模型，仅根据明确算法选择对应证书文件名/校验规则。证书缺失、私钥不匹配、算法不支持均立即失败，不能降级为明文。

## 5. 模块职责

### rdb-config

- 读取 CLI、环境变量和配置文件。
- 校验并生成服务端能力集合或客户端偏好配置。
- 记录最终生效的来源和摘要，不记录私钥内容。

### tls_cert

- 接收已解析配置和证书路径。
- 创建 SSL_CTX。
- 加载指定 CA、证书和私钥。
- 按握手选中的 profile 应用对应 cipher suite 和证书链。
- 执行客户端/服务端 TLS handshake。
- 统一释放 SSL/SSL_CTX。

不再负责配置优先级、目录扫描、CA 列表动态选择或旧布局兼容。

### rpc-handshake/rpc-io

- 保留 `TIME` 编解码和 `NEGOTIATE` 编解码。
- 负责 session 初始化、plain/TLS 回调切换和清理。
- `TIME` 不触发 TLS 升级。
- `NEGOTIATE` 成功后才允许业务层继续收发。

### rdbcomm/aio-speed/dmsbtex/libobk

- 只负责构造模块配置和调用 session API。
- 所有业务网络 I/O 走 session read/write。
- 不直接调用 TLS 库、不重复实现握手、不保存全局 fd 映射。

## 6. 清理策略

所有连接采用统一 cleanup 出口：

```text
记录首个错误
  → 停止后续业务 I/O
  → rpc_hs_session_cleanup()
  → 关闭 fd（由连接所有者执行一次）
  → 释放私有上下文/日志文件
  → 返回首个错误
```

握手失败、证书加载失败、业务收发失败和关闭报文失败都必须经过该出口。

## 7. 可观测性

统一记录：`role`、`stage`、`operation`、`mtls`、`algorithm`、`ca_cn`、`peer`、`result`。禁止记录私钥和完整证书内容。TIME 和 NEGOTIATE 的日志必须能明确区分。

## 8. 风险与取舍

- 删除历史兼容会使旧证书目录和旧客户端失效，这是本任务的明确取舍。
- TIME 保持独立意味着它不会验证 mTLS 证书；其用途限于时间同步，不得作为业务连接复用。
- 不使用全局锁和 fd 映射，连接状态必须由 session/调用栈显式持有。
