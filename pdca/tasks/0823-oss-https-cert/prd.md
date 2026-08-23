# oss：支持 HTTPS 使用证书 — 规格文档

## 问题陈述

- **现状**: aio-oss（`oss/cmd`，Go `net/http` + minio/mux）以 `http.ListenAndServe` 明文 HTTP 提供服务（`oss/cmd/oss.go:listenAndServe`），无 TLS，传输无加密、无服务端身份认证。
- **目标**: oss 服务在**单一端口**上以 HTTPS（TLS）对外提供加密信道与身份认证。
- **差距**: 缺 TLS 监听入口与证书加载逻辑；需与同仓库证书约定（`/opt/aio/cfg/certs/`）对齐来源，但算法采用标准 TLS（不引入国密）。

## 解决方案

在 `oss/cmd` 增加证书加载与 TLS 监听：TLS/算法配置可来自**配置文件 rdb.conf**（与 rdbcomm 等 C 模块共用，经 `--config` 指定，默认 `/opt/aio/cfg/rdb.conf`，对齐 T0367 的 dmsbtex 从配置文件读取模式）或 CLI flag；按算法前缀解析证书（默认 `ed25519` → `<cert-dir>/ed25519_host.crt`/`ed25519_host.key`，对齐 C 模块 `CERT_FILE_ED25519_HOST` 前缀约定；亦可显式 `--cert-path`/`--key-path` 覆盖）；在既有的单一 `--port` 上以 `http.ListenAndServeTLS` 启动 HTTPS（不再提供明文 HTTP）。证书缺失/非法/算法不支持则 fail-closed 整体启动失败。

## Seam 分析

### 测试接缝
- 边界层：`oss/cmd/oss.go` 的证书加载与 TLS 监听装配（抽取为 `buildTLSConfig(certPath, keyPath) (*tls.Config, error)` 与单端口 TLS 监听装配），纯函数/小装配可测。
- 已有覆盖：`oss/test/build_oss.sh` 验收 `xmake build oss` 与 `--version`/`--help`/独立 `go build` 回归。
- 新增覆盖：`oss/cmd/oss_https_test.go`（Go 表驱动测试）覆盖：
  - 合法自签 RSA/ECDSA 证书 → 单端口 HTTPS 监听成功、HTTPS 客户端握手成功；
  - 同一端口对明文 HTTP 客户端握手失败（TLS 必需）；
  - 证书缺失/非法 → `buildTLSConfig` 返回错误（fail-closed 装配失败）；
  - 弱密码套件客户端握手被拒（验证 MinVersion/密码套件约束）。
- 隔离策略：测试内用 `crypto/x509`/`crypto/ecdsa`(或 rsa) 生成临时自签证书写入临时文件，避免依赖仓库外 SM2 证书；不依赖真实网络可达性（监听 127.0.0.1 ephemeral 端口）。

### 声明的测试接缝
- seam: oss/cmd/oss_https_test.go -> oss/cmd/oss.go

### 验收可测性
- 每个 AC 有明确 pass/fail（监听成功/握手结果/返回错误）。
- fail-closed 通过 `buildTLSConfig` 返回错误断言，避免真实进程退出测试。
- 算法约束通过受限客户端握手成功/失败双向验证。

## 用户故事

1. 作为运维，我想要 oss 以 HTTPS 在单一端口提供加密服务，以便对象存储传输不被窃听/篡改且配置简单。
2. 作为安全审计，我想要 OSS 仅协商 TLS1.2/1.3 + AES256-GCM，且证书缺失即拒绝启动，以便消除明文与弱套件风险。

## 实现决策

- **修改模块**: 仅 `oss/cmd`（`oss/cmd/oss.go` 增加 flag 与单端口 TLS 监听；`oss/cmd/config.go` 增加 `CertPath`/`KeyPath` 字段与 `BuildConfig` 解析；`oss/cmd/oss_https_test.go` 新增测试）。不改动其他 C 模块。
- **新 flag（CLI 最高优先级，覆盖配置）**:
  - `--config`（string，默认 `/opt/aio/cfg/rdb.conf`；可用环境变量 `RDB_CONFIG` 覆盖）：rdb.conf 配置文件路径（INI）。
  - `--cert-dir`（string，默认 `/opt/aio/cfg/certs/`）：证书目录，存放按算法前缀命名的证书材料。
  - `--tls-algorithm`（string，默认 `ed25519`）：证书算法前缀；当前支持 `ed25519`（Go 标准 `crypto/tls` 可加载）；`sm2` 国密（Go 标准库不支持）→ fail-closed。
  - `--cert-path`（string，可选）：显式指定服务端证书（PEM）；设置后忽略按前缀/配置解析。
  - `--key-path`（string，可选）：显式指定服务端私钥（PEM）；设置后忽略按前缀/配置解析。
  - 既有 `--port` 即为唯一监听端口，现以 TLS 提供 HTTPS（不再有明文 HTTP 监听）。
- **与其他工具一致的 4 层解析模型（对齐 rdbcomm `sec_resolve`）**: 工具段 `[oss]` → 全局段 `[security]` → 环境变量 → 默认值。OSS 复用 C 模块的段名与键名（rdb-config.h）：工具段键 `mtls_enable`(SEC_TOOL_MTLS_KEY)、`tls_algorithm`(SEC_TOOL_ALGORITHM_KEY)；全局段键 `tls_enable`(SEC_GLOBAL_TLS_KEY)、`ciphersuites`(SEC_GLOBAL_CIPHERSUITES_KEY)、`cert_dir`(SEC_GLOBAL_CERT_DIR_KEY)；环境变量 `OSS_TLS_ALGORITHM`(OSS_TLS_ALGORITHM_ENV)、`OSS_TLS_ENABLE`(OSS_TLS_ENABLE_ENV)、`RPC_TLS_CERT_DIR`(RPC_TLS_CERT_DIR_ENV，与 C 共用)。
- **配置文件 rdb.conf（INI）格式**（与 rdbcomm/dmsbtex 同款）:
  ```ini
  [oss]                                  ; 工具段，优先级最高
  mtls_enable = 1
  tls_algorithm = TLS_AES_256_GCM_SHA384 ; AES→ed25519 证书前缀；SM4(国密)→sm2(Go 不支持→fail-closed)

  [security]                             ; 全局段，工具段缺省时回退
  tls_enable = 1
  ciphersuites = TLS_AES_256_GCM_SHA384
  cert_dir = /opt/aio/cfg/certs
  ```
  OSS 用**最小 INI 解析器**（支持 `[oss]`→`[security]` 两级查找，不引入新 Go 依赖）读取上述键。
- **配置解析优先级（从高到低）**: CLI flag（`--cert-path`/`--key-path`/`--tls-algorithm`/`--cert-dir`）> 配置（工具段 `[oss]` > 全局段 `[security]` > 环境变量）> 内置默认（`ed25519` 前缀 / `/opt/aio/cfg/certs`）。证书路径：显式 `--cert-path/--key-path` > 配置 `cert_path/key_path`（若有） > `<cert-dir>/<前缀>_host.crt|key`（前缀由 `--tls-algorithm` 或配置 `tls_algorithm`/`ciphersuites` 映射：TLS_AES_256_GCM_SHA384→ed25519，TLS_SM4_GCM_SM3→sm2）。
- **加载与装配**: 抽取 `loadTLSConfigFile(path) (*TLSConfigFromRDB, error)`（最小 INI 解析 rdb.conf：先查工具段 `[oss]`，缺省回退全局段 `[security]`，取 `mtls_enable`/`tls_algorithm`(或 `ciphersuites`)/`cert_dir`；文件缺失/段缺失不报错、返回零值）、`resolveCertPaths(config, fileCfg) (certPath, keyPath string)`（按上述 4 层优先级解析；`tls_algorithm`/`ciphersuites` 经 `mapCiphersuiteToPrefix` 映射为证书前缀）与 `buildTLSConfig(certPath, keyPath) (*tls.Config, error)`（调用 `tls.LoadX509KeyPair`；失败返回错误；`tls.Config{ MinVersion: TLS1.2, CipherSuites: [TLS_AES_256_GCM_SHA384, TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256] }`，其中 AES256-GCM 优先，后两者为 HTTP/2 必需套件（仍属 AES-GCM，非弱 CBC），缺失会导致 Go `ListenAndServeTLS` 因 h2 协商失败报错）。`serverMain` 中：
  1. `loadTLSConfigFile` → `resolveCertPaths`（CLI flag 优先、配置分层次之、内置默认垫底）；`buildTLSConfig` 失败（缺失/非法/算法不支持）→ `log` 错误并 `return err`（进程退出非 0，服务不起）；
  2. 否则在单一 `addr=:port` 上 `go http.ListenAndServeTLS(addr, certPath, keyPath, router)`（替换原 `http.ListenAndServe`）。
- **TLS 配置**: `tls.Config{ Certificates:[]tls.Certificate{cert}, MinVersion: tls.VersionTLS12 }`；`CipherSuites` 限定 AES256-GCM：`tls.TLS_AES_256_GCM_SHA384`（TLS1.3）、`tls.TLS_ECDHE_RSA_AES256_GCM_SHA384`、`tls.TLS_ECDHE_ECDSA_AES256_GCM_SHA384`（TLS1.2）。Curves 默认（X25519/P256）。不启用国密。
- **单端口 HTTPS**: 仅一个 TLS 监听复用既有 `router`（minio/mux）；原明文 `http.ListenAndServe` 移除；信号退出逻辑不变。对到达该端口的明文 HTTP 请求，TLS 握手失败（连接被拒/重置），无明文服务。
- **fail-closed**: 证书缺失/格式错误/公私钥不匹配 → `buildTLSConfig` 返回错误，`serverMain` 返回该错误（`Main` 中 `os.Exit(1)`），服务整体不起，避免半加密/明文状态。
- **默认证书文件名**: 按算法前缀 `ed25519_host.crt`/`ed25519_host.key`（位于 `/opt/aio/cfg/certs/`，对齐 C 模块 `CERT_FILE_ED25519_HOST`；ED25519 证书，Go 标准 `crypto/tls` 原生支持）。运维可经 `--tls-algorithm` 切换前缀，或显式 `--cert-path`/`--key-path` 覆盖。
- **测试证书**: 单测内生成临时自签 ECDSA/RSA 证书（PEM 写入 `t.TempDir()`），不依赖仓库外证书。

## 测试决策

- 仅测外部行为（HTTPS 可连、单端口 TLS 必需、fail-closed、算法约束），不测路由内部逻辑（沿用既有）。
- 被测模块：`oss/cmd/oss.go` 的 `buildTLSConfig` 与监听装配。
- 先例：`oss/test/build_oss.sh` 的构建/版本回归验收。

## 验收标准

- [ ] AC-1: 给定合法证书（默认 `ed25519_host.crt`/相应私钥，或测试内自签 ED25519/RSA 证书），OSS 在单一 `--port` 启动 TLS 监听；HTTPS 客户端（信任 CA 或 `InsecureSkipVerify`）GET 返回正常响应（非连接拒绝/握手失败）。
- [ ] AC-2: 单端口 TLS 必需 —— 对到达该端口的明文 HTTP 客户端握手失败（无明文服务）；即同一端口仅提供 HTTPS。
- [ ] AC-3: 证书缺失 fail-closed —— `--cert-path` 指向不存在文件（或默认 `ed25519_host.crt` 缺失）时 `buildTLSConfig` 返回错误、`serverMain` 启动失败（进程退出非 0），服务不起。
- [ ] AC-4: 证书非法 fail-closed —— cert/key 内容损坏或公私钥不匹配时 `buildTLSConfig` 返回错误、启动失败。
- [ ] AC-5: 算法/版本约束 —— 受限客户端仅协商 `TLS_AES_256_GCM_SHA384`（TLS1.3）握手成功；受限为弱套件（如 `TLS_RSA_WITH_AES_128_CBC_SHA`）的客户端握手被拒；协商最低版本不低于 TLS1.2；`--tls-algorithm=sm2`（国密）因 Go 标准库不支持而 fail-closed（启动失败）。
- [ ] AC-6: 构建/回归 —— `xmake build oss` 成功；`oss/test/build_oss.sh` 既有验收仍 PASS。
- [ ] AC-7: 配置文件获取 TLS/算法 —— 提供含 `[security]` 段的 rdb.conf（tls_enable/ciphersuites/cert_dir），OSS 从该文件获取 TLS/算法配置并据此启动 HTTPS；`--config` 缺失或文件不存在时回退 CLI flag 与内置默认（不报错）。

## 范围外

- 国密 SM4_GCM_SM3（需引入 gmssl/第三方，单独评估，不在本期）。
- 客户端证书校验（mTLS）——本期单向服务端 TLS。
- 证书签发/自动轮换——仅消费既有证书文件。
- 明文 HTTP 并存/重定向——本期单端口仅 HTTPS。
- C 模块（dmsbtex/libobk/rpc）的 TLS 改造——不在本期。

## 备注

- 关联前身任务：T0259（0814-oss-https-support，“oss https 支持 + 性能重测报告”，仍停在 plan 且空 PRD，active）——本次为续作/重做，决策以本任务为准；经用户确认由“HTTP+HTTPS 并存”调整为“单一端口 HTTPS”。
- 关联任务：T0366（TLS 证书 P2）、T0367（dmsbtex init_sbt_config 读 mTLS 键）、T0328（dmsbtex libobk mTLS 握手）；证书目录约定沿用 `/opt/aio/cfg/certs/`。
- 性能重测：前身 T0259 标题含“性能重测报告”；本期 AC 不强制性能基线与重测，若需可在 Act 阶段补充（列为 follow-up 候选）。
