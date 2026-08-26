# oss：参数化开启 HTTPS，默认 HTTP

## 问题陈述

T0368 为 aio-oss 引入 HTTPS 时采用**强制模式**：`serverMain` 无条件构建 TLS 配置并 `ListenAndServeTLS`，证书缺失/非法即 fail-closed 整体启动失败。部署方没有任何手段让服务以明文 HTTP 运行，导致无证书环境（开发、测试、内网模拟场景）服务完全不可用。

需求：HTTPS 变为**可选开关**——默认纯 HTTP 启动；显式配置后才启用 HTTPS（保持既有 fail-closed 语义）。

## 方案概述

在既有 4 层配置模型上新增 **TLS 开关解析链**：

1. **CLI flag**：新增 bool flag `--tls`（默认 false），并利用 urfave/cli v3 的 inverse-bool 支持 `--no-tls` 显式关闭，实现三态：未设置 / 显式开 / 显式关。
2. **环境变量**：`OSS_TLS_ENABLE_ENV`（base.go 已预留常量，本次启用）。
3. **rdb.conf**：`[oss] mtls_enable` 工具段优先 → `[security] tls_enable` 全局段回退（与证书解析的段序一致）。布尔值宽松解析：`1/true/yes/on`（大小写不敏感）为真，其余非空值为假。
4. **默认值**：false（HTTP）。

生效优先级对齐现有 `chooseStr`：CLI > env > rdb.conf > 默认。

行为分发：
- 开关关闭（默认）：**完全跳过 TLS 链路**——不解析证书路径、不加载证书、不做 fail-closed 校验，`http.ListenAndServe` 明文监听。
- 开关开启：走 T0368 既有路径——`buildServingTLS` 构建受限 TLS 配置（TLS1.2+ / AES-GCM / h2 套件齐全），失败 fail-closed 退出；成功则单端口 HTTPS 监听。
- 启动日志明确打印监听模式（`listening HTTP on :port` / `listening HTTPS on :port`）。

## 用户故事

1. 作为部署工程师，在内网无证书环境运行 `aio-oss server`，服务以 HTTP 正常启动提供 S3 模拟接口。
2. 作为部署工程师，在需要加密链路的环境运行 `aio-oss server --tls`，服务以 HTTPS 启动；证书缺失时启动失败并给出明确错误（fail-closed 不静默降级）。
3. 作为运维人员，通过 rdb.conf 的 `tls_enable` 或环境变量统一下发开关，无需改动启动命令。

## 实现决策

| 决策点 | 结论 | 理由 |
|--------|------|------|
| 开关载体 | CLI + env + rdb.conf 全链路 | base.go 已预留常量；与证书解析同构 |
| flag 命名 | `--tls`（inverse: `--no-tls`） | 对齐名词型 kebab-case 风格；三态可表达 |
| HTTP 模式 TLS 逻辑 | 完全跳过 | 零文件依赖、零开销；预检告警引入隐性依赖无收益 |
| 显式开 HTTPS + 证书缺失 | 保持 fail-closed | 用户要求加密却静默降级明文更危险；沿用 T0368 行为 |
| 默认值变更 | 接受破坏性变更（强制 HTTPS → 默认 HTTP） | 内部 emulator，部署方可控；默认可用性优先 |
| 配置键归属 | `[oss] mtls_enable` > `[security] tls_enable` | 与证书目录/算法解析段序一致，复用既有键常量 |

## 测试决策

单元测试覆盖全部 AC（复用 oss_https_test.go 的自签证书 helper 与 httptest 基建）；构建回归走 xmake + build_oss.sh；不做端到端真实部署验证。

## 范围外

- 客户端侧 TLS 行为变更
- 国密 sm2 支持（维持 Go 标准库限制下的 fail-closed）
- http+https 双端口并存监听
- mTLS 双向认证
- rdbcomm 等 C 工具侧任何改动

## Seam 分析

### 声明的测试接缝

- seam: oss/cmd/oss_https_test.go -> oss/cmd/tls.go
- seam: oss/cmd/oss_https_test.go -> oss/cmd/oss.go

## 备注

- T0368 知识资产 `knowledge/oss/oss_https_tls.md` 中 h2 套件坑位（CipherSuites 必须保留 AES_128_GCM_SHA256）在本任务中不得回退。
- 历史任务 T0259（0814-oss-https-support）处于 Pending 但功能已被 T0368 覆盖，本任务完成后建议顺带清理其状态。

## 验收标准

- [ ] AC-1: 运行 `aio-oss server --port <p>`（不带 --tls、env 与 rdb.conf 无开关配置）后向该端口发明文 GET，返回 200 且日志含 `listening HTTP`
- [ ] AC-2: 运行 `aio-oss server --tls --cert-path <crt> --key-path <key>` 后 TLS 握手成功（GET=200），同一端口明文请求被拒（400）
- [ ] AC-3: 运行 `aio-oss server --tls` 且证书缺失/非法时进程以非零退出码终止，错误信息包含"加载证书/私钥失败"
- [ ] AC-4: 设置环境变量 OSS_TLS_ENABLE=true 后不带 --tls 启动且证书齐备，得到 HTTPS 监听；rdb.conf `[security] tls_enable=true` 同样生效；`[oss] mtls_enable=true` 优先于全局段；`--no-tls` 可显式压过 env/conf 层的开启回到 HTTP
- [ ] AC-5: `go test ./cmd`（oss 目录，vendor 模式）全绿，含新增开关用例；`xmake build oss` 与 `oss/test/build_oss.sh` 回归通过
