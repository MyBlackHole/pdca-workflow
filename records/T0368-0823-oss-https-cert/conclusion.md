# T0368 验收结论（Check）

## 任务
oss（aio-oss，Go 服务）支持 HTTPS 使用证书：单 TLS 端口、按算法前缀解析证书（默认 `ed25519_host.crt`/`ed25519_host.key`）、从 rdb.conf 按 4 层模型（[oss]>[security]>环境变量>默认）读取 TLS/算法配置，标准 TLS1.2/1.3 + AES-GCM，证书缺失/非法/sm2 国密 fail-closed。

## 实现产物
- `oss/cmd/tls.go`：最小 INI 解析 `parseRDBConfig`、4 层优先级 `resolveCertPaths`、`mapCiphersuiteToPrefix`、`buildTLSConfig`（MinVersion=TLS1.2，仅 AES-GCM 套件，含 HTTP/2 必需的 AES_128_GCM_SHA256）、`buildServingTLS`。
- `oss/cmd/oss.go`：新增 `--config/--cert-dir/--tls-algorithm/--cert-path/--key-path` flag；`serverMain` 先 `buildServingTLS`，失败则返回错误（进程 `os.Exit(1)`，服务不起）；`serveHTTPS` 单端口 `ListenAndServeTLS`。
- `oss/cmd/config.go`：Config 增加 TLS 字段与 `BuildConfig` 读取。
- `oss/cmd/base.go`：复用 rdb-config.h 段名/键名/环境变量常量（对齐 rdbcomm sec_resolve）。
- `oss/cmd/oss_https_test.go`：AC-1~AC-7 单测。

## 验证结果
- 单元：`go test ./cmd` 全绿（HTTPS 握手成功、明文被拒、缺失/非法证书 fail-closed、弱套件被拒、rdb.conf 4 层解析、前缀映射）。
- 构建/回归：`xmake build oss` 成功；`oss/test/build_oss.sh` RESULT ALL PASS；`cd oss && go build -mod=vendor` 回归通过（AC-6）。
- 运行时：`aio-oss server --cert-path /opt/aio/cfg/certs/host.crt --key-path /opt/aio/cfg/certs/host.key --port 8448` 单端口 HTTPS `GET=200`、明文 `HTTP=400`；缺失证书进程 `exit=1`（AC-1/AC-2/AC-3）。

## 收敛
收敛映射见 evidence/convergence-map.final.json，AC-1~AC-7 全覆盖，validate-convergence 通过（valid=True）。

## 结论
实现满足 PRD 全部验收标准，建议 verdict=confirmed 进入 Act（知识沉淀 + 归档）。
