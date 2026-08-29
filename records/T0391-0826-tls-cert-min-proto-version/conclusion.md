---
schema: pdca.asset/v1
id: T0391-0826-tls-cert-min-proto-version
phase: check
source_ids: [build-log, test-log, diff-log, convergence-map]
---

## 上下文
T0388/T0389/T0390 收尾后"mTLS 全面深度审查"发现 **F1（中危）**：`libs/tls_cert.c` 生产 TLS 上下文创建仅 `SSL_CTX_new(TLS_method())`，未显式设置最低协议版本，依赖 OpenSSL 默认与"仅配置 TLS1.3 套件"的隐式约束。本任务予以显式锁定。

## 假设与结果
- 假设：在 `tls_cert_slot_create` 新增 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)` 即可将全部生产上下文（server/client 共用该函数）最低版本锁为 TLS1.3，且不破坏既有 TLS1.3 握手。
- 结果：构建通过；新增回归测试 `tls_cert_min_proto_version_enforced` 断言 AES/SM4 两个 slot 的 SSL_CTX 最低版本均为 `TLS1_3_VERSION` 并通过；原有 19 个用例全部通过，无回归。

## 分析
- **AC-1** ✅ tls_cert.c 所有 `SSL_CTX_new` 创建的上下文均显式设最低版本 TLS1.3，libs 构建通过（build-log）
- **AC-2** ✅ 新增回归用例强制校验 ctx 最低版本 == TLS1_3_VERSION（AES+SM4 两 slot），全部 20 用例 PASSED（test-log）
- **AC-3** ✅ 仅新增一行版本下限设置 + 一个测试函数，未改动套件/算法/验证回调逻辑；git diff 显示 13 行新增、0 删除（diff-log, build-log）

测试可判别性：无修复时 OpenSSL4 默认最低为 TLS1_2_VERSION，断言 `== TLS1_3_VERSION` 必失败，故确实验证了修复生效。

## 适用边界
- 仅作用域为 libs/tls_cert.c 生产上下文；tls_keygen.c 测试工具已设 TLS1_3_VERSION，未改动。
- 未解决 F2（CRL 强制）/F3（GET_TIME 豁免）/F4（dmsbtex 强制分散）/F5（subject 白名单），均属独立后续任务。

## 下一轮建议
- 建议合并提交（待用户"提交"指令）；F2–F5 视安全优先级另开任务。
