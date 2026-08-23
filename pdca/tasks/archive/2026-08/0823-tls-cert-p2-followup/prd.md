# TLS 证书处理 P2 安全增强（跟进 T0365）

## 问题陈述

T0365 已完成 `libs/tls_cert.c` 四类缺陷修复（AC-1 双向身份绑定 / AC-2 ciphersuites
fail-closed / AC-3 ca_cn 确定性 / AC-4 客户端 ctx 缓存并发复用），四模块经统一接口
间接受益。但代码审查与 T0365 结论指出以下事项留待 P2 跟进：

1. **证书热加载/轮换缺失**：当前证书/密钥变更需重启进程，生产环境不友好，且
   AC-4 的客户端 ctx 缓存一旦建立会长期复用，证书轮换后无法生效。
2. **CRL/OCSP 吊销检查缺失**：fail-closed 目前仅校验"链有效 + 对端 CN 匹配"，
   未校验证书是否已被吊销，存在实时信任链缺口（revoked-but-valid-chain 仍可握手）。
3. **错误码前缀未归一**：`libs/tls_cert.c` 错误码风格不统一（部分 `TLS_CERT_ERR_*`、
   历史/调用方混用裸负数），T0364 follow-up 建议统一前缀便于排障（P2-6/前缀归一）。
4. **审计未记录对端 CN**：握手审计日志未记录对端证书 CN，事件溯源与合规困难
   （P2-5，顺带优化，设 AC 但不强约束性能）。

## 目标

对 `libs/tls_cert.c` 及调用方做 4 项 P2 增强，补齐生产级证书治理能力，保持
fail-closed 精神与"四模块经统一接口受益、不逐模块改动"的约束。

## 范围

- **在范围**：AC-1~AC-4 四项增强 + 单测覆盖；调用约定/错误码文档化（前缀归一表）。
- **不在范围（本次）**：mTLS 全链路压测平台化、证书自动签发（属 tls_keygen 范畴）、
  多 CA 交叉信任模型。

## 验收标准

- [ ] AC-1: 证书热加载/轮换——`libs/tls_cert.c` 提供 ctx 级 reload 入口（服务端
  `server_tls_ctx`/`sbt_server_ctx` 与客户端缓存槽均支持），证书文件变更后下次
  握手使用新证书/密钥；客户端缓存槽在 reload 时按 key 失效并重建。单测：构造初始
  ctx，替换证书文件后触发 reload，验证后续握手指纹/CN 来自新证书。
- [ ] AC-2: CRL/OCSP 吊销检查——握手验证阶段在"链有效 + CN 匹配"之外，增加
  证书吊销校验（优先 OCSP、回退 CRL，按配置开关）；被吊销证书即使链有效也
  fail-closed 拒绝。单测：构造"链有效但已吊销"的对端证书，握手须被拒绝。
- [ ] AC-3: 错误码前缀归一——`libs/tls_cert.c` 全部错误返回统一为 `TLS_CERT_ERR_*`
  枚举（去裸负数/历史前缀），调用方错误判读改为枚举比较。单测：扫描所有返回路径
  确认均为 `TLS_CERT_OK` 或 `TLS_CERT_ERR_*`，无混杂裸负数。
- [ ] AC-4: 审计对端 CN——握手成功/失败审计日志记录对端证书 subject CN（与 AC-1
  身份绑定呼应），便于溯源。单测：构造一次握手，验证审计日志含对端 CN 字段。

## Seam 分析

### 声明的测试接缝

- seam: `libs/tests/tls_cert_test.c` -> `libs/tls_cert.c`（单元：reload 生效、吊销拒绝、
  错误码枚举、审计 CN 记录）
- seam: `libs/tls_cert.c` -> `libs/tls_cert.h`（错误码前缀归一后调用方编译/语义校验）

## 范围外

- 证书自动签发与轮换策略引擎（建议另立 tls_keygen 任务）
- 多 CA 交叉信任与桥接模型
- OCSP stapling 服务端缓存（可作为 AC-2 后续增强）

## 备注

- 沿用 T0358 fail-closed、T0365 双向身份 pin 范式；AC-2 是其自然延伸（信任链完整性）。
- 四模块调用方（rdbcomm / dmsbtex / libobk / rpc）经 `tls_cert_*` 接口间接受益，
  AC-1 reload 入口与 AC-3 错误码变更若触及调用点则一并适配，不逐模块重构。
- 参考 `knowledge/tls/client-ctx-cache-concurrency.md`（客户端缓存并发模式，
  AC-1 reload 须与之兼容：reload 失效缓存槽时持锁并等待 refcount 归零）。
