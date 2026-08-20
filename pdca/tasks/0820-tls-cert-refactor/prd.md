# 重构 tls_cert 模块 — 规格文档

## 问题陈述

- **现状**: `libs/tls_cert.{c,h}` 使用全局单例 `g_ctx`，进程内只能承载一个 client 或 server 的 SSL_CTX，无法同时持有多套证书链；客户端通过 `tls_cert_select_cert_callback` 动态遍历服务端下发的 CA 列表猜测证书；存在两套全局缓存（CA/host）+ 两个 rwlock；SM2 与普通证书分支在初始化函数中交织；头文件含 6 个无任何外部调用者的接口；错误码取值零散（-1..-16 中段跳跃）；模块自身直接 getenv 证书路径类环境变量，配置逻辑与配置层职责重复。
- **目标**: tls_cert 收敛为"接收已解析配置 → 创建 SSL_CTX → 加载证书 → 握手 → 释放"的确定性模块；服务端可同时持有 SM4/AES 两套独立 SSL_CTX；客户端使用单证书显式路径；配置解析与 getenv 全部移出 tls_cert，由调用方填充 options 传入；无死代码与未用接口；错误码语义类型稳定、取值紧凑。
- **差距**: 全局单例→多 profile 并存；动态证书猜测→显式路径；内部 getenv→options 参数；缓存+锁→确定性加载；死代码/未用接口清理；错误码重排。

## 解决方案

tls_cert 对外暴露两个 options 结构体驱动的初始化入口：`tls_cert_init_server` / `tls_cert_init_client` 一次传入 profile 数组（每个 profile 含算法+ca_cn+CA+证书+私钥，上限 2 个，SM4/AES），返回单个 `tls_cert_ctx`（内部 map 按算法键控各 profile 的 SSL_CTX+证书）。客户端与服务端共用 profile 数组语义，客户端可持有不同算法的同一服务端证书。`mtls_enabled` 由 tls_cert 内部判断：未启用则返回 OK 且不创建上下文。握手接口按 `algorithm` 参数查 ctx 内 map 选用对应 SSL_CTX 完成 TLS 升级。调用方自行解析各自配置（env/config/CLI）填充 options、持有 ctx、负责释放。

## Seam 分析

### 测试接缝

- 测试边界在 `libs/tls_cert.{c,h}` 公共 API：init 成功/失败、多 profile 并存、单证书、错误码、握手。
- 已有测试覆盖 init 基础、SM2 链、ciphersuites、mTLS/SM2 握手（`tls_cert_test.c`）；需改为 options 调用方式并新增多 profile 并存断言。
- 外部依赖隔离：证书文件使用现有测试证书目录（tests/certs）；Socket 握手用本地回环；不引入外部网络依赖。

### 声明的测试接缝

- seam: `libs/tests/tls_cert_test.c` -> 证书链加载、TLS 初始化、多 profile 并存、错误码与握手
- seam: `libs/tests/rpc_handshake_test.c` -> 服务端 TLS 可用性与握手联动

### 验收可测性

- 每个 AC 有明确 pass/fail 信号（运行测试/构建/grep）。
- 边界条件（profile 缺失、非法算法、证书缺失）可独立构造。

## 用户故事

1. 作为服务端进程，我想要一次初始化同时持有 SM4 与 AES 两套证书链，以便不同客户端按算法选择对应 mTLS 连接而无需重启。
2. 作为客户端进程，我想要通过 profile 数组传入同一服务端不同算法的证书配置，以便按握手协商算法选择对应证书完成 mTLS。
3. 作为调用方，我想要通过 options 结构体传入已解析配置并持有 ctx，以便 tls_cert 不缓存证书、不读环境变量、职责清晰。
4. 作为维护者，我想要删除无外部调用者的接口并整理错误码，以便 API 面收敛、语义清晰。

## 实现决策

**新增/修改的模块**：`libs/tls_cert.{c,h}`（重写核心逻辑与公共 API）。

**模块接口定义**：

```c
typedef struct {
    const char *algorithm;   /* TLS_SM4_GCM_SM3 / TLS_AES_256_GCM_SHA384 */
    const char *ca_cn;       /* CA 名（服务端匹配与 client CA 列表下发；客户端选定 CA） */
    const char *ca_cert;     /* CA 证书路径（PEM） */
    const char *cert;        /* 主机证书路径 */
    const char *key;         /* 主机私钥路径 */
} tls_cert_profile_t;

typedef struct {
    int mtls_enabled;
    tls_cert_profile_t profiles[2];  /* 上限 2：SM4 + AES */
    size_t profile_count;
} tls_cert_client_options_t;         /* 客户端可多 profile：不同算法同一服务端 */

typedef struct {
    int mtls_enabled;
    tls_cert_profile_t profiles[2];  /* 上限 2：SM4 + AES */
    size_t profile_count;
} tls_cert_server_options_t;         /* 服务端多 profile 并存 */

typedef struct tls_cert_ctx tls_cert_ctx_t;  /* 内部 map：algorithm -> {SSL_CTX, X509, EVP_PKEY} */

int tls_cert_init_client(const tls_cert_client_options_t *opts,
                         tls_cert_ctx_t **ctx_out);
int tls_cert_init_server(const tls_cert_server_options_t *opts,
                         tls_cert_ctx_t **ctx_out);
void tls_cert_cleanup(tls_cert_ctx_t *ctx);
SSL_CTX *tls_cert_get_ssl_ctx(tls_cert_ctx_t *ctx,
                              const char *algorithm);
SSL *tls_cert_client_handshake(tls_cert_ctx_t *ctx, int fd,
                               const char *algorithm, tls_cert_result_t *result);
SSL *tls_cert_server_handshake(tls_cert_ctx_t *ctx, int fd,
                               const char *algorithm, tls_cert_result_t *result);
```

**技术澄清**：

- `tls_cert_ctx` 内部为 map（key=算法名），每个算法 profile 独立 `SSL_CTX` + `X509` + `EVP_PKEY`；client/server 各自独立 ctx，进程内可并存；tls_cert 不缓存、不持有超出 ctx 生命周期外的证书状态。
- 多 profile：init 时一次为每个 profile 创建 SSL_CTX 并加载证书链，握手时按 `algorithm` 参数查 ctx 内 map 选用；`algorithm` 为 NULL 时使用 ctx 内首个 profile。
- 客户端多 profile：同一客户端可持有不同算法的同一服务端证书，握手时按算法选择。
- `client_handshake_for_cn` 语义由调用方按 ca_cn 选择 profile 后调用 `tls_cert_client_handshake(ctx, fd, algorithm, result)` 替代，无目录扫描、无动态猜测。
- SM2 分支：由 profile 中 algorithm 判定（含 `TLS_SM`），不再读环境变量判断；SM2 证书链由 profile 显式路径加载。
- 证书路径全部由调用方解析填入 options；tls_cert 不 getenv、不推导 cert_dir、不做目录扫描。
- 错误码：重排为紧凑负值序列，`TLS_CERT_OK=0` 不变；异常类型（LOAD_CA/LOAD_CERT/LOAD_KEY/SSL_CREATE/INVALID_PARAM/NO_CERT/NO_CONFIG）语义不变，仅取值调整；删除 `TLS_CERT_IS_LOCAL/NOT_LOCAL/LOAD`（随 `verify_is_local*` 接口删除）。
- 删除接口：`tls_cert_detach_ssl`、`tls_cert_set_checkname`、`tls_cert_verify_is_local`、`tls_cert_verify_is_local_x509`、`tls_cert_init_from_env`、`tls_cert_get_global_ctx`、`tls_cert_server_available`，及旧双参 `init_client_with_options`/`init_server_with_options`/`init_client_from_env`/`init_server_from_env`。
- 删除内部：`tls_cert_select_cert_callback`（动态 CA 列表遍历）、CA/host 全局缓存与 rwlock、注释掉的 `verify_is_local` 校验块、`get_checkname`/`get_local_host_id`、全局 `g_ctx` 单例。
- rdb-config 现有 `sec_*` 签名与实现保持不变。
- 调用方适配：rdbcomm/rdbcommd/rpc-client/rpc-main/sbt-session/libobk/dmsbtex/fs-backup/timed_net_key 改为构造各自 options 并解析证书路径后传入、持有 ctx 执行握手；getenv 由调用方处理；rpc-handshake 持自身 server ctx 判断可用性。

**架构决策**：options 驱动的确定性证书加载（删除动态选择与配置职责混入）。记入 ADR。

**数据模型变更**：无持久化数据变更。

**API 合约**：上述公共接口为唯一对外 API；行为契约见验收标准。

## 测试决策

- 仅测外部行为：通过公共 API 构造场景，断言返回值与握手结果，不测内部实现细节。
- 被测模块：`libs/tls_cert.{c,h}` 及其调用方适配后的集成行为。
- 现有先例：`tls_cert_test.c`、`rpc_handshake_test.c` 的断言风格与测试证书目录复用。

## 验收标准

- [ ] AC-1: 运行 tls_cert 单元测试，得到服务端一次初始化返回单个 `tls_cert_ctx`，其内部 map 同时保有 SM4 与 AES 两个算法 profile 的独立 SSL_CTX（按算法可分别获取验证）；任一 profile 证书缺失仅该 profile 失败、不降级明文。
- [ ] AC-2: 运行 tls_cert 单元测试，得到客户端多 profile（不同算法同一服务端证书）初始化成功、按算法选择对应 SSL_CTX；非法算法/缺失证书/缺失 CA 返回对应错误码（类型与文档一致）。
- [ ] AC-3: 运行 tls_cert 单元测试与 mTLS 握手测试，得到普通证书与 SM2 证书的成功/失败矩阵通过，且删除的 7 个接口（detach_ssl/set_checkname/verify_is_local/verify_is_local_x509/init_from_env/get_global_ctx/server_available）在代码库中无任何引用（grep 计数为 0）。
- [ ] AC-4: 运行全部调用方（rdbcomm/rdbcommd/rpc/sbt-session/libobk/dmsbtex/fs-backup/timed_net_key）的构建与相关集成握手测试通过，旧双参与 from_env 初始化入口无残留引用（grep 计数为 0）。
- [ ] AC-5: 运行静态检查（编译警告、`git diff --check`、缓存/锁扫描），得到 tls_cert.c 无全局证书缓存、无 rwlock、无 getenv 直接调用，构建无新增警告。

## 范围外

- 不修改 RPC 握手报文字段与协议版本。
- 不改变 rdb-config 的 `sec_*` 配置接口签名与实现。
- 不改变 rdbcomm/aio-speed/dmsbtex/libobk 的业务调用方式与 ABI（仅初始化入口适配）。
- 不引入新的全局锁或 fd 映射。
- 不实现证书自动生成、轮换或在线重载。

## 备注

- 与 T0331「简化 SBT/RPC mTLS 证书与算法路径」为独立任务，本任务聚焦 tls_cert 模块自身；T0331 保持独立 plan。
- 错误码重排涉及测试断言同步更新；`rpc_handshake_test.c` 仅用 `== TLS_CERT_OK` / `!= TLS_CERT_OK`，不受重排影响。