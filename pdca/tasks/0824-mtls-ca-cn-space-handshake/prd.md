# 【B】mTLS 握手失败：CA CN 含空格被客户端校验拒绝 — 规格文档（用户裁决版）

## 问题陈述

- **现状**: `xmake run aio-speed ... --mtls-enable 1` 报 `tls_cert_init_client failed: cert_dir=/opt/aio/cfg/certs/ algorithm=TLS_SM4_GCM_SM3 ca_cn=My SM2 Root CA`。
- **目标**: CN 命名规范收敛为"无空格"，从生成源头杜绝非法 CN 进入部署链路；配合证书重签使 mTLS 握手恢复。
- **差距**: keygen 不校验 CN 字符集，允许生成含空格 CN（示例即 "My SM2 Root CA"），而客户端 `tls_cert_ca_cn_valid()` 白名单 `[A-Za-z0-9._-]` 拒绝之——三方不一致。

## 根因（已取证）

`libs/tls_keygen.c` ca/host 证书生成对 `-n <CN>` 无字符集校验 → 存量 CA subject CN="My SM2 Root CA" → 服务端原样下发 → 客户端 `tls_cert_ca_cn_valid`（libs/tls_cert.c:21）拒空格 → `TLS_CERT_ERR_INVALID_PARAM` → 握手失败。

## 解决方案（用户裁决）

1. **keygen 强制无空格**：生成 ca/host 时校验 CN 符合客户端同款白名单 `[A-Za-z0-9._-]`，违规时报错退出并列出合法字符集与示例；
2. **客户端校验保持不变**（严格白名单为规范基准）；
3. **配套动作**：用修正后的 keygen 重签 CA/host 证书并部署，实机验证握手；
4. SM2 文件名布局缺口（sm2_host.* vs host.*）**本轮不处理**（用户裁决），记入已知问题。

## Seam 分析

### 测试接缝
- 新增 keygen CN 校验单元测试，沿用 libs/tests 既有 C 测试风格（临时目录 + 断言宏）。
- Mock/Stub：无需网络，纯参数级校验测试。

### 声明的测试接缝
- seam: libs/tests/tls_keygen_test.c -> libs/tls_keygen.c

### 验收可测性
- 每个 AC 独立 pass/fail：单测断言 + CLI 退出码 + 实机握手输出。

## 用户故事

1. 作为 `运维人员`，我想要 keygen 在生成时就拒绝非法 CN，以便错误在源头暴露而非部署后在握手时才发现。
2. 作为 `开发者`，我想要生成器与客户端共享同一套 CN 合法性定义，以便两端永不打架。

## 实现决策

- keygen 内新增/复用与 `tls_cert_ca_cn_valid` 同规则的校验函数（字符集逐字一致，注释互引防漂移）。
- 错误信息含合法字符集说明与改名示例。
- 帮助文本示例名同步改为无空格形式（如 My_SM2_Root_CA）。

## 测试决策

- 先写失败用例（含空格 CN 被 keygen 拒绝）再实现（TDD）。
- 回归：libs/tests 全部 + rdbcomm/tests 握手相关。

## 验收标准

- [ ] AC-1: 新增单测证明 keygen CN 校验：含空格 CN 返回错误，合法 CN 通过（含边界字符 . _ -）
- [ ] AC-2: 运行 `tls-keygen ca -n "My SM2 Root CA" -a sm2` 类命令以非零退出并输出合法字符集提示
- [ ] AC-3: 使用重签的无空格 CN 证书部署后，运行 `aio-speed -h <host> -p <port> -c "ls -alh" --mtls-enable 1` 完成 mTLS 握手并返回命令结果
- [ ] AC-4: libs/tests 与 rdbcomm/tests 既有用例全部保持通过

## 范围外

- SM2 证书文件名布局回退（用户裁决不处理；已知问题：客户端仅找 cert_dir/<ca_cn>/host.*，SM2 keygen 输出 sm2_host.*，部署时需自行摆放为 host.*）
- 协议层 CN 编码、服务端下发逻辑变更
- 存量带空格证书的自动迁移

## 备注

- 复现环境：/opt/aio/cfg/certs/ 已有 "My SM2 Root CA/"（sm2_host.*）与 sm2_ca.crt；重签部署步骤将在 Do 阶段产出操作记录。
- 关联任务：F-139 TLS/mTLS 全栈（T0386 主线 3/4）。
