---
schema: pdca.asset/v1
id: ontology:pattern/oss-https-tls
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/oss-https-tls/1.0.0
summary: oss HTTPS / TLS 配置模型
source_task: T0368
relations:
  specializes: [ontology:pattern]
  guides: [ontology:entity/tls-configuration, ontology:entity/tls-session]
attributes:
  - name: applicability
    desc: aio-oss 由明文 HTTP 支持 HTTPS 使用证书
    constraint: ""
    testable_signal: 单端口 HTTPS、算法前缀解析、4 层优先级、受限 TLS 保留 h2 套件、证书缺失 exit=1
---

# oss HTTPS / TLS 配置模型（T0368）
# oss HTTPS / TLS 配置模型（T0368）

## 背景
aio-oss（Go 服务，二进制 `aio-oss`）原本仅提供明文 HTTP（`http.ListenAndServe`）。T0368 让其支持 HTTPS 使用证书：单 TLS 端口、按算法前缀解析证书、并从 `rdb.conf` 读取 TLS/算法配置，与其他 C 工具（rdbcomm/dmsbtex）的配置逻辑保持一致。

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
