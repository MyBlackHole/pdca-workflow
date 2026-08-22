# 设计文档 — tls_cert 初始化 API 完善

## 1. 背景与约束

- 沿用 T0332 的 `tls_cert_ctx` 单一上下文 + 内部双 slot 模型（`SM4/AES` 各一 `SSL_CTX`），不引入全局单例/lock；`options` 层不再暴露 `profiles[2]`。
- 配置解析职责已外移：`tls_cert` 不 `getenv`，由 `rpc_init_config` / `sec_resolve_*` 在调用方完成，`tls_cert_init_*` 仅消费 `options`。
- 证书文件命名由 `libs/common.h:19` 统一：`ca.crt/ca.key/host.crt/host.key` 与 `sm2_ca.crt/sm2_host.crt/sm2_host.key`，并新增 `ed25519` 前缀常量 `ed25519_ca.crt/ed25519_host.crt/ed25519_host.key`（与旧无前缀并存，新优先旧回退，唯一常量源）。

## 2. 总体架构

```
[Tool CLI] --tool_algorithm--> [g_rpc_config.tls_algorithm] --hs_algorithm_name--> [options.algorithm]
[Handshake Resp] --result.ca_cn--> [options.ca_cn] --\
                                                    +--> tls_cert_build_client_profile --> tls_cert_init_client --> tls_cert_ctx{ slot[SM4], slot[AES] }
[sec_resolve] --cert_dir--> [options.cert_dir] -----/                  |
                                                                        +--> TLS_SSL{ ssl, slot* } --> SSL_read/write
[sec_resolve] --cert_dir--> [server options.cert_dir] --> tls_cert_build_server_profiles --> tls_cert_init_server --> tls_cert_ctx
```

- 服务端：`cert_dir` 必填即走 `build_server_profiles` 产生 2 个 profile，`algorithm` 固定双算法；无 `profiles` 兼容路径。
- 客户端：`cert_dir + algorithm + ca_cn` 三元组唯一路径走 `build_client_profile` 产生单 profile；移除 `profiles[0]` 显式兼容路径，不兼容旧写法。

## 3. 模块与接口

### 3.1 libs/tls_cert.{c,h} 与 libs/common.h

- `common.h:19` 为唯一常量源：保留 `CERT_FILE_CA/HOST/HOST_KEY`（旧无前缀）并新增 `CERT_FILE_ED25519_CA="ed25519_ca.crt"`、`CERT_FILE_ED25519_HOST` 等（新有前缀），注释“新优先旧回退”。
- 精简为 `tls_cert_server_options_t{mtls_enabled, cert_dir}` 与 `tls_cert_client_options_t{mtls_enabled, cert_dir, algorithm, ca_cn}`，删除 `profiles[2]/profile_count`，`tls_cert_profile_t` 仅作 `build_server_profiles` 内部产出。
- `tls_cert_build_server_profiles:113`：输入 `cert_dir`，输出 2 个 `out_profiles` 及 6 buffer，`out_count=2`；`AES` 侧 `ca/cert/key` 均有前缀→无前缀回退（`stat` 探测或依次 `load` 尝试）。
- `tls_cert_build_client_profile:122`：`ca` 按 `algorithm` 区分（`SM4->sm2_ca.crt`，`AES->ed25519_ca.crt` 优先回退 `ca.crt`）；`cert/key` 为 `cert_dir/ca_cn/host.*` 且 `ca_cn` 必填，非法字符 `INVALID_PARAM`。
- `tls_cert_init_server/client`：仅 `cert_dir` 路径，空 `cert_dir` 直接 `INVALID_PARAM`；`slot_create:95` 拆 `LOAD_CERT/LOAD_KEY` 且对 `ED25519/AES` 的三文件依次尝试有前缀→无前缀，首个可加载即成功。

### 3.1.1 libs/tls_keygen.c 统一

- `handle_create/handle_ca/handle_sign` 中 `snprintf("%s_host.key", algo)` 硬编码改为复用 `common.h` 常量（`CERT_FILE_ED25519_*` / `CERT_FILE_SM2_*` / `CERT_FILE_*`），生成仍优先新前缀格式，读取/校验侧同样走 `tls_cert` 的双格式兼容加载。

### 3.2 rpc/rpc-config.cpp 与 rpc/rpc-config.h

- `rpc_init_config:168` 补 `cert_dir` 的 `sec_resolve_str(NULL,NULL,SEC_GLOBAL_SECTION,SEC_GLOBAL_CERT_DIR_KEY,RPC_TLS_CERT_DIR_ENV,DEFAULT_CERT_DIR)`，使 `rpc/main.cpp:417` 可命中双算法；`ca_cert/server_cert/server_key` 字段保留但不再被 `tls_cert` 消费（过渡期仅作兼容宏，不读）。

### 3.3 rpc/main.cpp 与 rdbcomm/rdbcommd-main.c

- 仅 `server_opts{mtls_enabled, cert_dir}` 唯一形态，无 `else` 回退；删除 `hs_algorithm_name(tool_algorithm)` 单算法甄别与 `ca_cert/server_cert/server_key` 手填；空 `cert_dir` 直接 `INVALID_PARAM` 不建连。

### 3.4 rpc/rpc-io.cpp

- `rpc_handshake_client_negotiate:133` 仅 `cert_dir+algorithm+ca_cn` 单路径（无 `else if(client_cert)` 显式分支）：
  ```cpp
  if(!cert_dir[0] || !ca_cn[0] || !algorithm[0]) return -1; // INVALID_PARAM
  opts={mtls_enabled=1, cert_dir, algorithm, ca_cn};
  // 统一 tls_cert_init_client/handshake/cleanup
  ```
  删除栈上 `client_cert/key` 局部拷贝与 early return 重复块。

## 4. 时序

1. 进程启动：`rpc_init_config` / `sec_resolve` 填充 `cert_dir/tls_algorithm/ca_cert/...` → `g_rpc_config`。
2. 服务端 `StartRpcService`：`tls_cert_init_server({cert_dir})` → `ctx` 持有双 `SSL_CTX` → `SetServerTlsCtx`。
3. 客户端 `connect_server_session`：`rpc_handshake_client_negotiate` 先明文 `HANDSHAKE` → 收到 `resp.ca_cn/algorithm` → `tls_cert_init_client({cert_dir,algorithm,ca_cn})` → `tls_cert_client_handshake(ctx, fd, alg)` → `rpc_io_init_tls` 后续帧走 `SSL_read/write`。

## 5. 错误与降级

- 任一 profile `LOAD_CA/LOAD_CERT/LOAD_KEY/SSL_CREATE` 即 `tls_cert_cleanup(ctx)` 并 `*ctx_out=NULL`，不降级明文。
- `algorithm` 非法或 `ca_cn` 含非法字符→`INVALID_PARAM`，调用方 `ErrorLog` 并返回 `-1`，连接关闭。

## 6. 兼容性

- 无兼容：旧 `profiles[0] profile_count=1` 与 `hs_algorithm_name` 单算法写法不再编译通过，`cert_dir` 必填。
- `tls_cert_init_*_from_cert_dir` 零调用点但保留，标记为 `reserved`，不删。

## 7. 非目标

- 不改握手帧 `HS_FLAG_MTLS_REQUEST` / `ca_cn` 字段长度 `200`。
- 不改 `rdb-config` `sec_*` 签名。
- 不引入证书轮转/热重载。
- 不改 `tls_keygen` 生成文件的 `0600` 权限。
