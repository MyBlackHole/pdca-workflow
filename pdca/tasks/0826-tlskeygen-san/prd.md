# tls-keygen 签发证书缺失 SAN 导致 TLS 客户端校验失败

## 问题陈述

`libs/tls_keygen.c` 的 sign 流程签发 host 证书时只写入 basicConstraints/keyUsage/SKI/AKI 四个扩展，**无 Subject Alternative Name**。现代 TLS 客户端按 RFC 6125 仅以 SAN 做 hostname/IP 匹配（CN fallback 已废弃），导致：

- aio-oss 使用 tls-keygen 生成证书开启 `--tls` 后，`ossutil -e https://127.0.0.1:8080 ls oss://test1` 实测报错：
  `tls: failed to verify certificate: x509: cannot validate certificate for 127.0.0.1 because it doesn't contain any IP SANs`
- curl 同步警告 `certificate subject name '<uuid>' does not match target hostname '127.0.0.1'`

影响所有以严格客户端访问 tls-keygen 证书服务的场景。

## 方案概述

sign 子命令新增可选参数 `--san "<条目,条目,...>"` 与默认 SAN 集合：

- 默认集合 `DNS:localhost, IP:127.0.0.1, IP:::1`（最小回环集）：未传参时写入默认值，保证开箱生成的证书可被严格客户端校验（对齐 Go generate_cert.go 业界惯例）
- 条目采用 OpenSSL nconf 格式：`DNS:<域名>`、`IP:<地址>`（IPv4/IPv6）
- 显式传入 → 以 `X509V3_EXT_nconf_nid(NID_subject_alt_name, ...)` 写入 SAN 扩展并完全覆盖默认
- 非法条目（缺前缀/空段）在生成前即报错退出，不产出半成品证书

配套：SAN 条目校验做成纯函数（对齐既有 `cn_name_valid` 放置 common.c 的模式）供单测；帮助文本更新并提示"客户端 hostname 校验依赖 SAN，建议显式指定"。

已知第二层问题（用户裁决不处理）：签发 CA 未入系统信任库时客户端仍报 unknown authority，属部署侧信任分发操作；端到端验证用 Go 原生 `SSL_CERT_FILE` 环境变量指向 CA 打通，不改系统状态。

## 用户故事

1. 作为部署工程师，运行 `tls-keygen sign --san "DNS:localhost,IP:127.0.0.1" ...` 生成含 SAN 的 host 证书，ossutil 经 https IP 端点正常访问 aio-oss。
2. 作为运维人员，误传格式错误 SAN 时工具立即报错并说明期望格式，避免产出不可用证书。

## 实现决策

| 决策点 | 结论 | 理由 |
|--------|------|------|
| 默认 SAN | 回环最小集 DNS:localhost,IP:127.0.0.1,IP:::1；--san 完全覆盖 | 经建议采纳：默认产物可用是本 bug 修复的核心诉求，回环名无安全副作用，业界惯例一致 |
| 参数形态 | 单参逗号分隔 OpenSSL nconf 格式 | 与 openssl -addext 习惯一致，解析简单 |
| 非法输入 | fail-fast 报错不产证 | 半成品证书比失败更危险 |
| CA 不受信 | 不处理，验证用 SSL_CERT_FILE | 部署侧操作；Go 客户端原生支持该环境变量 |

## 测试决策

SAN 校验纯函数走 tls_keygen_test.c 既有 assert 框架扩展用例；证书内容断言用 openssl -text 输出检查；端到端（aio-oss --tls + ossutil + SSL_CERT_FILE）作运行时验证登记 evidence。

## 范围外

- CA 证书入系统信任库/分发机制
- sm2 国密证书链客户端兼容性专项验证
- ossutil --skip-verify-cert 用法推广
- create/ca 子命令的 SAN（CA 证书无需 SAN）

## Seam 分析

### 声明的测试接缝

- seam: libs/tests/tls_keygen_test.c -> libs/tls_keygen.c

## 备注

- 复现记录（2026-08-26）：`xmake run aio-oss server --store /tmp/test-oss/ --port 8080 --tls` + `ossutil -e https://127.0.0.1:8080 ... ls oss://test1` → `x509: cannot validate certificate for 127.0.0.1 because it doesn't contain any IP SANs`；openssl -text 确认 /opt/aio/cfg/certs/ed25519_host.crt 无 SAN 且 CN 为 UUID。
- 修复后需重新签发 host 证书方可生效（旧证书不含 SAN 无法追溯修补）。

## 验收标准

- [ ] AC-1: `tls-keygen sign --san "DNS:localhost,IP:127.0.0.1,IP:::1"` 生成的证书经 openssl -text 可见对应 SAN 条目且与传入顺序一致
- [ ] AC-2: sign 不带 --san 生成的证书含默认回环 SAN 集（DNS:localhost, IP:127.0.0.1, IP:::1）；传非法值（如 `"localhost"` 缺前缀、空段）时进程非零退出且不产出证书文件
- [ ] AC-3: 端到端——以 --san 含 IP:127.0.0.1 的新证书启动 `aio-oss server --tls`，`SSL_CERT_FILE=<ca.crt> ossutil -e https://127.0.0.1:<port> ls oss://test1` 返回 bucket 列表（不再出现 SAN 类报错）
- [ ] AC-4: tls_keygen_test 新增 SAN 校验用例全绿；全量 `xmake test` 无回归（44+ 条 passed）
