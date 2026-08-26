---
schema: pdca.asset/v1
id: T3973-0826-tlskeygen-san
phase: check
source_ids: [san-cert-content, e2e-ossutil, e2e-ossutil-inspect, xmake-test-full-t3973, xmake-test-full-v2, convergence-map-v2]
---

## 上下文

用户以 `xmake run aio-oss server --tls` + `ossutil -e https://127.0.0.1:8080` 复现 TLS 校验失败。三重定位确认根因在仓库内 tls-keygen 工具：签发证书无 subjectAltName 扩展（RFC 6125 下客户端唯一匹配依据）。提交 28848cf6。

## 假设与结果

- 假设 1：sign 流程按 OpenSSL nconf 写入 SAN 即可满足客户端校验 → 成立，curl/ossutil 双客户端验证通过。
- 假设 2：默认回环集可保证开箱产物可用且无安全副作用 → 成立（DNS:localhost/IP 回环仅本机可解析）。
- 假设 3：--san 覆盖机制足以支撑生产域名声明 → 成立，顺序保持与 openssl -text 断言一致。

## 分析

- **AC-1** ✅ `sign --san "DNS:host.example.com,IP:10.0.0.5,DNS:localhost"` 生成证书 SAN 条目与传入完全一致（san-cert-content）
- **AC-2** ✅ 默认 sign 含回环集 DNS:localhost,IP:127.0.0.1,IP:::1；非法值 exit=1 且不产出证书文件（san-cert-content）
- **AC-3** ✅ 端到端：新证书启动 aio-oss --tls，SSL_CERT_FILE 指向签发 CA 后 ossutil ls oss://test1 成功返回（Object Number is: 0）；修复前同命令报 IP SANs 错误（e2e-ossutil / e2e-ossutil-inspect）
- **AC-4** ✅ tls_keygen_test 10 passed（含新增 san_ext_valid 5 组）；全量 xmake test 44 条 passed 零回归；build_oss.sh ALL PASS（xmake-test-full-t3973 / v2）

## 适用边界

- 仅覆盖 ed25519/sm2 host 证书签发；CA 证书无需 SAN 不涉及
- CA 未入系统信任库时仍会报 unknown authority——属部署侧信任分发（用户裁决不处理）
- 已部署旧证书不含 SAN 无法追溯修补，必须重新签发

## 下一轮建议

- 部署文档补充：tls-keygen 重签流程 + CA 信任分发（update-ca-certificates 或 SSL_CERT_FILE/--ca 配置）说明
- sm2 链 SAN 客户端兼容性可在国密 TLS 专项中顺带验证
- T0259 历史 Pending 任务清理仍待办

## verdict

{"outcome": "confirmed", "reason": "四条 AC 证据齐备（SAN 写入/覆盖/fail-fast/端到端 ossutil 走通/全量零回归），收敛 valid=True，双轴审查 Blocking=0，用户反馈的 inspect 缺失已补齐验证", "verdict_id": "T3973-0826-tlskeygen-san-check", "at": "2026-08-26T12:04:30+08:00"}
