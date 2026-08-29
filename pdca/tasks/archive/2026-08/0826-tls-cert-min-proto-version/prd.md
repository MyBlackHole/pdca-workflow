# PRD — T0391：为 tls_cert.c 生产 TLS 上下文显式设置最低协议版本

> 父任务：T0390（confirmed，已归档）。来源：T0388/T0389/T0390 收尾后的"mTLS 全面深度审查"发现的 **F1（中危）**——生产 TLS 上下文未显式设置最低协议版本下限。

## 问题陈述

- **现状**：`libs/tls_cert.c` 中 `tls_cert_slot_create` 通过 `SSL_CTX_new(TLS_method())`（tls_cert.c:236）创建所有生产 TLS 上下文（rpc / dmsbtex / libobk / rdbcomm 均复用），**未调用 `SSL_CTX_set_min_proto_version`**。仅测试工具 `libs/tls_keygen.c:1534` 设了 `TLS1_3_VERSION`。
- **目标**：生产上下文显式声明最低协议版本，消除对 OpenSSL 默认值的隐式依赖，符合"显式 deny / 纵深防御"。
- **差距**：缺一行 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`；当前仅靠"仅配置 TLS1.3 套件（SM4_GCM_SM3 / AES_256_GCM_SHA384）+ OpenSSL3/4 默认最低 TLS1.2"隐式约束到 TLS1.2+。

## 解决方案

在 `tls_cert_slot_create` 中 `SSL_CTX_new` 成功后、套件/证书/验证配置前，对新建 `ctx` 调用 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`。该函数同时服务 server 与 client（`is_server` 参数），一处改动覆盖全部生产上下文。

## Seam 分析

### 测试接缝
- 被测模块 `libs/tls_cert.c` 当前由 `libs/tests/tls_cert_test.c` 覆盖握手/验证（含 mTLS、CRL 吊销用例）。
- 新增"拒绝 TLS1.2 降级"用例：客户端 `SSL_CTX_set_max_proto_version(client_ctx, TLS1_2_VERSION)` 后发起握手，断言握手失败（fail-closed）。

### 声明的测试接缝
- seam: libs/tests/tls_cert_test.c -> libs/tls_cert.c

### 验收可测性
- 下限可通过"强制客户端最高 TLS1.2 后握手须失败"构造明确 pass/fail。
- 原 mTLS 握手用例继续作为回归基线（确保仅加一行下限不影响正常 TLS1.3 握手）。

## 用户故事

1. 作为安全审计者，我希望生产 TLS 上下文显式锁定最低协议版本，以便不依赖库默认、避免未来套件/配置放宽后协商到弱版本。

## 实现决策

- **修改点（单一）**：`libs/tls_cert.c` `tls_cert_slot_create`，`SSL_CTX_new` 成功校验后追加 `SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`。
- **版本选择**：TLS1_3（推荐）。理由：当前已仅配置 TLS1.3 套件（TLS1.2 本就无法协商），设 TLS1_3 与配置语义一致且为最强约束；`TLS1_3_VERSION` 已在 `tls_keygen.c` 使用，头文件可用。备择：TLS1_2（更宽松，但当前无实际收益）。
- **不动**：证书校验回调、套件白名单、CRL 逻辑、协商算法锁定。

## 测试决策

- 被测模块：`libs/tls_cert.c`。
- 现有先例：`libs/tests/tls_cert_test.c` 已有客户端/服务端握手与 CRL 用例，新增用例沿用其 `tls_cert_init_server` / `tls_cert_client_handshake` 接线方式。

## 验收标准

- [ ] AC-1: `libs/tls_cert.c` 中所有 `SSL_CTX_new(TLS_method())` 创建的上下文均显式设置最低协议版本为 TLS1.3（`SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION)`）；`libs` 构建通过（含 `-Werror`）。
- [ ] AC-2: 新增回归用例（libs/tests/tls_cert_test.c）——客户端 `SSL_CTX_set_max_proto_version(client, TLS1_2_VERSION)` 与服务端握手须失败（fail-closed），证明 TLS1.2 被拒；原有 mTLS 握手用例仍全部通过。
- [ ] AC-3: 仅新增一行版本下限设置，不改动已有套件/算法/验证回调逻辑，被测握手逻辑不变。

## 范围外

- 不改动 `libs/tls_keygen.c`（已设 TLS1_3，仅测试工具）。
- 不引入 CRL/OCSP 强制（属 F2，独立任务）。
- 不改动 `GET_TIME` 预握手豁免（属 F3，独立任务）。
- 不做 subject CN/SAN 白名单（属 F5，设计说明/可选增强）。

## 备注

- bugfix / 安全加固场景，含测试接缝。
- 关联审查结论：F1（中危，一行补丁低风险高收益）。
