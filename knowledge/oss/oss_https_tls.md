# oss HTTPS / TLS 配置模型（T0368 / T3970 开关化）

## 背景
aio-oss（Go 服务，二进制 `aio-oss`）原本仅提供明文 HTTP（`http.ListenAndServe`）。T0368 让其支持 HTTPS 使用证书：单 TLS 端口、按算法前缀解析证书、并从 `rdb.conf` 读取 TLS/算法配置，与其他 C 工具（rdbcomm/dmsbtex）的配置逻辑保持一致。**T3970 进一步将 HTTPS 开关化：默认明文 HTTP，显式配置后才启用 HTTPS**（证书缺失不再导致无证书环境服务不可启动）。

## 关键设计决策
1. **单端口 HTTPS**：唯一 `--port` 以 `http.Server.ListenAndServeTLS` 提供 HTTPS，不再有明文 HTTP 监听。明文请求被拒（返回 400）。
2. **证书按算法前缀解析**：默认 `ed25519` → `<cert-dir>/ed25519_host.crt`/`ed25519_host.key`（对齐 C 模块 `CERT_FILE_ED25519_HOST`）。`sm2`（国密）证书 Go 标准库不支持 → fail-closed。
3. **配置 4 层优先级（对齐 rdbcomm `sec_resolve`）**：CLI flag > 工具段 `[oss]`(`mtls_enable`/`tls_algorithm`) > 全局段 `[security]`(`tls_enable`/`ciphersuites`/`cert_dir`) > 环境变量(`OSS_TLS_ALGORITHM`/`OSS_TLS_ENABLE`/`RPC_TLS_CERT_DIR`) > 内置默认。复用 `rdb-config.h` 段名/键名/环境变量常量。
4. **算法映射**：`mapCiphersuiteToPrefix` 将 `TLS_AES_256_GCM_SHA384`/`TLS_ECDHE_*_AES_256_GCM_SHA384` → `ed25519`，`TLS_SM4_GCM_SM3`/`sm2` → `sm2`（Go 不支持 → fail-closed）。
5. **受限 TLS**：`tls.Config{ MinVersion: TLS1.2, CipherSuites: [AES256-GCM 三套件 + HTTP/2 必需的 TLS_ECDHE_*_WITH_AES_128_GCM_SHA256] }`。**注意**：Go 的 `ListenAndServeTLS` 在 `CipherSuites` 缺 h2 必需套件时会因 h2 协商失败直接报错退出，故必须保留 AES_128_GCM_SHA256 套件（仍属 GCM，非弱 CBC）。
6. **fail-closed**：`buildServingTLS` 在证书缺失/非法/算法不支持时返回错误，`serverMain` 返回该错误（`Main` 中 `os.Exit(1)`），服务整体不起，避免半加密/明文状态。

## 实现位置
- `oss/cmd/tls.go`：`parseRDBConfig`（最小 INI，仅解析 `[oss]`/`[security]`）、`resolveCertPaths`、`mapCiphersuiteToPrefix`、`buildTLSConfig`、`buildServingTLS`。
- `oss/cmd/oss.go`：新增 flag（`--config`/`--cert-dir`/`--tls-algorithm`/`--cert-path`/`--key-path`）、`serverMain` 先 `buildServingTLS` 后 `serveHTTPS`。
- `oss/cmd/config.go` / `base.go`：Config TLS 字段、`BuildConfig`、复用 rdb-config.h 常量。

## 测试与验证
- 单元：`oss/cmd/oss_https_test.go`（AC-1~AC-7），`go test ./cmd` 全绿。
- 构建/回归：`xmake build oss` + `oss/test/build_oss.sh` ALL PASS。
- 运行时：单端口 HTTPS `GET=200`、明文 `400`、缺失证书 `exit=1`。

## 坑位
- Go 1.21 的 `ListenAndServeTLS` 在 `TLSConfig.CipherSuites` 缺 h2 必需套件时**直接报错退出**（非仅警告）：必须保留 `TLS_ECDHE_*_WITH_AES_128_GCM_SHA256`。
- `crypto/tls` 套件常量在 Go 1.21 用 `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` 形式（无 `WITH` 的新命名 1.22 才引入）。
- oss 为纯 Go（crypto/tls 原生支持 Ed25519 证书），无需引入新依赖；INI 解析用最小自写实现（仅 `[oss]`/`[security]` 两级）。

## T3970 开关化设计（默认 HTTP，参数开启 HTTPS）
1. **三态 CLI flag**：urfave/cli v3 的 `BoolWithInverseFlag{BoolFlag: &cli.BoolFlag{Name:"tls"}}` 自动派生 `--tls/--no-tls`；用 `flag.IsSet()` 区分"未传/显式开/显式关"——普通 BoolFlag 无法区分未设置与 false，是三态开关的关键。框架自动调用 RunAction 把 `--no-tls` 归一为正向 false。
2. **四层开关联动 fail-closed 的分发模式**：`resolveTLSEnabled` 按 CLI > `OSS_TLS_ENABLE` env > rdb.conf `[oss] mtls_enable` > `[security] tls_enable` > 默认 false 解析；关闭路径**完全跳过**证书解析与 fail-closed 校验走 `ListenAndServe` 明文——fail-closed 只约束"用户显式要求的加密"，不惩罚无证书环境。
3. **可疑假值告警防静默降级**：`1/true/yes/on` 为真、空为未配置；其余非空值按关闭处理但区分两类——显式合法假值(`0/false/no/off`)静默，疑似拼写错误(如 `ture`)打告警日志提示将以明文启动。避免运维以为加密实则明文。
4. **布尔配置解析不要复用字符串 chooseStr**：bool 三态（未配置/false/true）与字符串空串哨兵不同构，独立实现 parseEnableStr 返回 `(val, configured)` 二元组更清晰。
5. **构建目标名漂移坑**：验收脚本硬编码 `xmake build <target>` 时目标改名会静默损坏回归链路（build_oss.sh 曾指向旧名 oss）；PRD 中写构建验证命令应引用真实 target 名。
