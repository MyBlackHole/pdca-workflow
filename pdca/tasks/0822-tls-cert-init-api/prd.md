# tls_cert 初始化 API 完善：服务端双算法 + cert_dir 构建 + 客户端 algorithm/ca_cn — 规格文档

## 问题陈述

- **现状**: `libs/tls_cert.{c,h}` 已提供 `tls_cert_server_options_t` / `tls_cert_client_options_t` 及 cert_dir 构建辅助，但服务端调用点（`rpc/main.cpp:417`、`rdbcomm/rdbcommd-main.c:352`）在无 cert_dir 时仍以单 profile 手填初始化，未固化双算法；客户端在 `rpc/rpc-io.cpp:133` 存在双分支重复组装；`TLS_KEYGEN_ALGO_ED25519` 存在无前缀（旧，`host.crt/host.key/ca.crt`）与有前缀（新，`ed25519_host.crt/ed25519_host.key/ed25519_ca.crt`）两种落盘格式，`tls_cert` 仅按无前缀加载导致旧/新混部时一方无法建连；`tls_keygen` 与 `tls_cert` 各自硬编码证书文件名（`common.h` 与 `tls_keygen.c:%s_host.key` 分散），无统一管理，新增算法或更名时两处易漂移。
- **目标**: tls_cert 初始化强制为 `cert_dir` 驱动且可测：服务端 `cert_dir` 驱动自动构建 SM4+AES 双算法链，客户端 `cert_dir + algorithm(hs_algorithm_name) + ca_cn(result.ca_cn)` 构建单 profile，不兼容旧 `profiles` 手填；`ED25519` 双格式均可加载（优先有前缀，缺失回退无前缀）；证书路径由 `common.h` 统一管理（集中常量+构建辅助），`tls_keygen` 与 `tls_cert` 共享同一套常量/拼接逻辑，不再各写一份。
- **差距**: 服务端双算法 cert_dir 固化缺口、客户端三元组收敛缺口、`profiles` 兼容移除、ED25519 双格式兼容缺口、路径统一管理缺口、API/错误码文档与 seam 契约化。

## 解决方案

tls_cert 强制 `cert_dir` 驱动并统一路径；本次增量完成：1) 精简 `tls_cert_server_options_t` 为 `{mtls_enabled, cert_dir}` 与 `tls_cert_client_options_t` 为 `{mtls_enabled, cert_dir, algorithm, ca_cn}`（移除 `profiles[2]/profile_count`）；2) 在 `common.h` 集中证书文件名常量（`CERT_FILE_*` 新增 `ed25519` 前缀版本）并提供统一构建辅助（`tls_cert` 与 `tls_keygen` 共用），消除两处硬编码；3) `tls_cert` 加载兼容 `ED25519` 双格式（优先 `ed25519_*` 有前缀，回退 `host.*`/`ca.*` 无前缀），`SM2` 保持 `sm2_*` 单格式；4) 服务端 `cert_dir` 双算法唯一路径与客户端 `cert_dir+algorithm+ca_cn` 唯一路径固化，删除显式分支；5) 以 seam 契约固化构建/兼容行为，确保“服务端双算法、`cert_dir` 构建、`algorithm/ca_cn` 透传、双格式兼容、路径统一”可回归。

## Seam 分析

### 测试接缝

- 在 `libs/tls_cert.{c,h}` 公共 API 边界：`tls_cert_build_server_profiles` / `tls_cert_build_client_profile` / `tls_cert_init_server` / `tls_cert_init_client` / 便捷初始化，按 algorithm 选 profile 与错误码分支。
- 已有 `libs/tests/tls_cert_test.c` 覆盖基础 init、SM2 链、mTLS 握手与多 profile 并存；需增量覆盖 cert_dir 驱动的双算法构建与客户端 algorithm+ca_cn 路径拼接（含 ca_cn 存在/缺失、algorithm 区分 ca 文件、非法参数）。
- 外部依赖隔离：证书文件使用现有测试证书目录（`libs/tests/certs`）；缺失场景用临时目录构造；不引入网络依赖，握手仍用本地回环/内存 BIO。

### 声明的测试接缝

- seam: libs/tests/tls_cert_test.c -> tls_cert.h
- seam: libs/tests/rpc_handshake_test.c -> rpc-handshake.h

### 验收可测性

- 每个 AC 有明确 pass/fail 信号（测试运行/编译/grep）。
- 边界条件（cert_dir 为空、ca_cn 为空/非法字符、algorithm 非法、证书文件缺失）可独立构造。
- 分层：cert_dir 构建为单元测试；多 profile 握手为集成测试；调用点收敛为静态检查（分支计数）。

## 用户故事

1. 作为服务端开发者，我想要通过 `tls_cert_server_options_t{ mtls_enabled, cert_dir }` 一次初始化即持有 SM4 与 AES 两套证书链（`cert_dir` 自动构建，无 `profiles` 手填），以便不同客户端按协商算法选择对应 mTLS 连接而无需按算法二选一重启。
2. 作为客户端开发者，我想要通过 `tls_cert_client_options_t{ mtls_enabled, cert_dir, algorithm, ca_cn }`（`algorithm` 来自工具参数 `hs_algorithm_name(tool_algorithm)`，`ca_cn` 来自握手响应 `result.ca_cn`）自动构建 `ca/cert/key` 路径（无 `profiles` 手填），以便无需手写路径即可完成对应算法与 CA 的 mTLS 连接。
3. 作为维护者，我想要移除旧显式 `profiles[0] profile_count=1` 兼容路径，实现 API 极简与单一职责，不再维护双分支。
4. 作为维护者，我想要消除 `rpc/rpc-io.cpp` 中客户端初始化的显式分支与栈局部指针组装，仅保留 `cert_dir+algorithm+ca_cn` 单一路，以可审计、可测试。
5. 作为运维/旧集群，我想要 `ED25519` 证书无论以 `host.crt/ca.crt`（旧无前缀）或 `ed25519_host.crt/ed25519_ca.crt`（新有前缀）落盘，`tls_cert` 均可加载成功（优先有前缀，回退无前缀），以便滚动升级不中断。
6. 作为维护者，我想要 `tls_keygen` 与 `tls_cert` 的证书文件名/路径拼接逻辑在 `common.h` 统一管理，新增算法或更名仅改一处，不再两处硬编码漂移。

## 实现决策

- **新增/修改的模块**: `libs/common.h`（集中证书文件名常量，新增 `ED25519` 前缀版本 `ed25519_ca.crt/ed25519_host.crt/ed25519_host.key` 并保留旧无前缀作回退，提供统一注释）；`libs/tls_cert.{c,h}`（精简 API 删 `profiles[2]/profile_count`，仅 `cert_dir` 驱动，加载兼容双格式，复用 `common.h` 常量）；`libs/tls_keygen.c`（生成/CA/签发路径改用 `common.h` 统一常量，不再 `%s_host.key` 硬编码）；`rpc/main.cpp`、`rdbcomm/rdbcommd-main.c`（服务端唯一形态）；`rpc/rpc-io.cpp`（客户端唯一形态）；`libs/tests/tls_cert_test.c`（增量构建/兼容用例）。
- **模块接口定义**:

```c
/* 内部辅助：仅 build_server_profiles 产出双 profile，不再作为 options 字段 */
typedef struct {
    const char *algorithm;
    const char *ca_cn;
    const char *ca_cert;
    const char *cert;
    const char *key;
} tls_cert_profile_t;

typedef struct {
    int mtls_enabled;
    const char *cert_dir;   /* 必填，证书根目录，如 /opt/aio/cfg/certs/ */
    const char *algorithm;  /* 必填，工具参数 hs_algorithm_name(tool_algorithm) */
    const char *ca_cn;      /* 必填，服务端协商 result.ca_cn */
} tls_cert_client_options_t;

typedef struct {
    int mtls_enabled;
    const char *cert_dir;   /* 必填，证书根目录，如 /opt/aio/cfg/certs/ */
} tls_cert_server_options_t;

int tls_cert_init_client(const tls_cert_client_options_t *opts, tls_cert_ctx_t **ctx_out);
int tls_cert_init_server(const tls_cert_server_options_t *opts, tls_cert_ctx_t **ctx_out);
int tls_cert_build_server_profiles(const char *cert_dir, tls_cert_profile_t out_profiles[2], size_t *out_count,
                                   char out_ca0[512], char out_cert0[512], char out_key0[512],
                                   char out_ca1[512], char out_cert1[512], char out_key1[512]);
int tls_cert_build_client_profile(const char *cert_dir, const char *algorithm, const char *ca_cn,
                                  char *ca_out, size_t ca_sz, char *cert_out, size_t cert_sz,
                                  char *key_out, size_t key_sz);
int tls_cert_init_server_from_cert_dir(const char *cert_dir, tls_cert_ctx_t **ctx_out);
int tls_cert_init_client_from_cert_dir(const char *cert_dir, const char *algorithm, const char *ca_cn, tls_cert_ctx_t **ctx_out);
```

- **技术澄清**:
  - 初始化唯一路径：`cert_dir` 必填（服务端/客户端均不再支持显式 `profiles` 数组，空 `cert_dir` 直接 `INVALID_PARAM`，不回退）。
  - 服务端 cert_dir 构建约定：`SM4 -> sm2_ca.crt/sm2_host.crt/sm2_host.key`，`AES -> ed25519_ca.crt/ed25519_host.crt/ed25519_host.key 有前缀优先、回退 ca.crt/host.crt/host.key 无前缀`（`algorithm` 固定 `TLS_SM4_GCM_SM3` / `TLS_AES_256_GCM_SHA384`，内部双 slot 固定 2，`options` 不再暴露 `profile_count`）。
  - 客户端 cert_dir 构建约定：`ca` 按 `algorithm` 区分（SM4->`sm2_ca.crt`，AES->`ed25519_ca.crt` 优先回退 `ca.crt`）；`cert/key` 为 `cert_dir/ca_cn/host.*`（`ca_cn` 必填且仅 `[A-Za-z0-9._-]`，非法即 `INVALID_PARAM`；`host.*` 在 `ca_cn` 目录内与算法无关，加载时对 AES 的 `ca` 与 `host` 均做双格式回退）。
  - 统一管理：`common.h` 为唯一常量源（`CERT_FILE_*` 含 `ed25519` 前缀与旧无前缀并存，注释“新优先旧回退”），`tls_cert` 与 `tls_keygen` 均 `include "common.h"` 后复用常量，不再各自 `snprintf("%s_host.key", algo)` 硬编码；新增算法仅在 `common.h` 增常量与映射。
  - 双格式兼容：`tls_cert` 的 `slot_create` 对 `ED25519/AES` 的 `ca_cert/cert/key` 加载时依次尝试有前缀→无前缀，首个存在且可加载即成功；`tls_keygen` 生成侧仍优先有前缀新格式，但检验/加载侧同样兼容双格式。
  - 错误码：`TLS_CERT_OK=0, INVALID_PARAM=-1, LOAD_CA=-2, LOAD_CERT=-3, LOAD_KEY=-4, SSL_CREATE=-5, NO_CERT=-6, NO_CONFIG=-7` 保持不变；`cert_dir/algorithm/ca_cn` 任一为空或非法直接 `INVALID_PARAM`；证书文件缺失对应 `LOAD_*` 且 `ctx==NULL` 不降级明文。
  - 不兼容旧示例：原 `profiles[0].algorithm=hs_algorithm_name(tool_algorithm), ca_cert=g_rpc_config->ca_cert, cert=g_rpc_config->server_cert, key=g_rpc_config->server_key, profile_count=1` 写法不再编译通过，调用点必须改为 `tls_cert_server_options_t{mtls_enabled=1, cert_dir=g_rpc_config->cert_dir}`。
  - 不引入全局缓存/lock；`tls_cert` 不 `getenv`，配置解析由调用方完成。
- **架构决策**: cert_dir 驱动的确定性路径构建 + 多 profile 并存（不做运行时猜测与配置内省）。不新增 ADR（沿用 T0332 的 options 驱动决策），必要时在 convergence 备注中留痕。
- **数据模型变更**: 无持久化变更。
- **API 合约**: 上述 6 个初始化/构建接口为本次契约核心；握手接口 `tls_cert_{client,server}_handshake(ctx, fd, algorithm, result)` 按 algorithm 选 ctx 内 profile 的行为不变。

## 测试决策

- 仅测外部行为：通过公共 API 构造场景断言返回值与 ctx 内 profile 状态，不测内部实现细节。
- 被测模块：`libs/tls_cert.{c,h}` 及其调用方适配后的行为。
- 现有先例：`tls_cert_test.c` 的断言与证书目录复用；`rpc_handshake_test.c` 的 algorithm 映射先例复用。
- 新增用例：cert_dir 双算法构建返回值与路径后缀断言、algorithm 区分 ca 文件断言、ED25519 双格式回退断言（有前缀优先、无前缀回退）、`tls_keygen` 与 `tls_cert` 路径常量一致性断言、非法 `cert_dir/algorithm/ca_cn` 错误码断言；不再覆盖显式单 profile 兼容路径。

## 验收标准

- [ ] AC-1: `tls_cert_build_server_profiles(cert_dir)` 返回 2 个 profile，`out_ca0` 后缀为 `sm2_ca.crt` 且 `algorithm==TLS_SM4_GCM_SM3`、`out_ca1` 后缀为 `ca.crt` 且 `algorithm==TLS_AES_256_GCM_SHA384`；`out_cert0/out_key0` 与 `out_cert1/out_key1` 分别为对应 host 文件路径；非法 `cert_dir`（NULL/空串/NULL out 参数）返回 `TLS_CERT_ERR_INVALID_PARAM`。
- [ ] AC-2: `tls_cert_build_client_profile(cert_dir, algorithm, ca_cn)` 在 `algorithm==TLS_SM4_GCM_SM3` 时 `ca_out` 后缀为 `sm2_ca.crt`，在 `TLS_AES_256_GCM_SHA384` 时为 `ca.crt`；`ca_cn` 必填且 `cert_out/key_out` 后缀为 `ca_cn/host.crt` / `host.key`；`ca_cn` 为空或含非法字符（`/`/`..`）时返回 `TLS_CERT_ERR_INVALID_PARAM`；`cert_dir/algorithm` 非法亦 `INVALID_PARAM`。
- [ ] AC-3: `tls_cert_init_server({mtls_enabled=1, cert_dir="<tmp>"})` 在包含双算法证书文件的临时 cert_dir 下返回 `TLS_CERT_OK` 且 `ctx` 内可分别通过两种 algorithm 获取独立 `SSL_CTX`（`aes_ctx != sm_ctx && != NULL`）；任一 profile 证书缺失时整体返回 `LOAD_CA`/`LOAD_CERT`/`LOAD_KEY` 且 `ctx==NULL`（不降级明文）；`cert_dir` 为空直接 `INVALID_PARAM`。
- [ ] AC-4: `tls_cert_init_client({mtls_enabled=1, cert_dir, algorithm, ca_cn})` 在 `algorithm` 与 `ca_cn` 透传下构建的 profile 可成功初始化（`tls_cert_get_ssl_ctx(ctx, algorithm)!=NULL`）；`algorithm` 非法或 `cert_dir`/`ca_cn` 为空时返回 `TLS_CERT_ERR_INVALID_PARAM`；不再支持显式 `profiles[0] profile_count=1` 旧写法（编译期移除）。
- [ ] AC-5: 运行构建与静态检查，得到 `rpc/main.cpp` 与 `rdbcomm/rdbcommd-main.c` 的服务端初始化仅 `cert_dir` 唯一路径（无 `hs_algorithm_name` 单算法甄别与 `ca_cert/server_cert/server_key` 手填），`rpc/rpc-io.cpp` 中客户端初始化仅 `cert_dir+algorithm+ca_cn` 单路径（无显式 `client_cert/client_key` 分支与栈局部组装），且 `libs/tls_cert.c` 无 `getenv`/全局缓存/lock 且 `grep -rn "profiles\[" libs/tls_cert.h` 为 0（`profile_count` 仅内部辅助可残留）。
- [ ] AC-7: `ED25519` 双格式兼容：分别在仅含无前缀 `ca.crt/host.crt/host.key` 与仅含有前缀 `ed25519_ca.crt/ed25519_host.crt/ed25519_host.key` 的临时 `cert_dir` 下，`tls_cert_init_{server,client}` 均可成功（有前缀优先，无则回退），且混合落盘（`ca` 有前缀而 `host` 无前缀）亦可加载。
- [ ] AC-8: 路径统一管理：`grep -rn "CERT_FILE_" libs/common.h` 含 `ed25519` 前缀常量，`grep -rn "%s_host\.key\|%s_ca\.crt" libs/tls_keygen.c` 为 0（不再硬编码 `snprintf("%s_host.key", algo)`），`grep -rn "CERT_FILE_" libs/tls_cert.c libs/tls_keygen.c` 均指向 `common.h` 常量。
- [ ] AC-6: 运行现有测试套件 `tls_cert_test` 与 `rpc_handshake_test`（若有）通过，无回归；新增 cert_dir 构建单测已纳入 `tls_cert_test.c` 并随套件一次性通过。

## 范围外

- 不修改握手报文字段与协议版本。
- 不改变 `rdb-config` 的 `sec_*` 配置接口签名与实现。
- 不改变业务调用方式与 ABI（仅初始化入口适配）。
- 不实现证书自动生成、轮换或在线重载。
- 不新增全局锁或 fd 映射。

## 备注

- 与 T0332 的关系：T0332 已完成 options 驱动的多 profile 重构与全局清理；本任务为其后续增量，聚焦 cert_dir 双算法与 algorithm/ca_cn 的 API 契约固化与调用点收敛。
- 错误码与便捷初始化（`tls_cert_init_*_from_cert_dir`）为已有能力，本任务做行为固化与测试补齐，不做取值变更。
