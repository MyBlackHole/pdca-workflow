# 【F】tls_cert_init_client 按算法获取对应证书名 — 规格文档（用户裁决版）

## 问题陈述

- **现状**: 客户端 profile 构建对 cert/key 固定使用无前缀 `cert_dir/<ca_cn>/host.{crt,key}`，CA 固定取自 cert_dir 根；keygen 按算法输出 `{algo}_host.*` 且实际部署以每 CA 一目录组织（如 `/opt/aio/cfg/certs/MySM2RootCA/` 内为 sm2_host.*）。SM2 客户端必须人工改名摆放才能工作。
- **目标**: `tls_cert_init_client` 按算法获取对应证书名，SM2 链整体采用 `cert_dir/<ca_cn>/` 子目录 + 算法前缀命名（含 CA）；ED25519 保持现状不动。
- **差距**: 证书名选择不感知算法；SM2 的 CA 与主机证书均未纳入子目录前缀布局。

## 解决方案（用户裁决）

1. **SM2（TLS_SM4_GCM_SM3）**：build_client_profile 返回
   - CA: `cert_dir/<ca_cn>/sm2_ca.crt`
   - cert: `cert_dir/<ca_cn>/sm2_host.crt`
   - key: `cert_dir/<ca_cn>/sm2_host.key`
   仅认带前缀名，不做下沉。
2. **ED25519（AES_256_GCM_SHA384）**：路径构建与 slot_create 下沉回退（pick_ed25519_*）完全保持现状。
3. 服务端布局不变；rdb-config sec_tls_client_cert_paths 与 Go 侧 oss/cmd/tls.go 的一致性完成处置（同步或记录差异）。

## Seam 分析

### 测试接缝
- libs/tests/tls_cert_test.c 新增用例：SM2 路径断言（函数级）+ 临时目录仅 sm2_* 三件套的 init 集成用例；ED25519 既有用例作为回归锚点。

### 声明的测试接缝
- seam: libs/tests/tls_cert_test.c -> libs/tls_cert.c

### 验收可测性
- 每个 AC 独立 pass/fail：路径字符串断言 + init 返回码 + 回归零失败。

## 用户故事

1. 作为 `运维人员`，我想要 keygen 生成的 SM2 证书按 CA 目录原名直放即用，以便不再手工改名。
2. 作为 `开发者`，我想要 SM2 与 ED25519 的布局差异显式化且有测试锚定，以便演进时不互相破坏。

## 实现决策

- 前缀常量复用 common.h 既有 CERT_FILE_SM2_CA/CERT_FILE_SM2_HOST/CERT_FILE_SM2_HOST_KEY。
- SM2 分支内聚于 build_client_profile（slot_create 不新增 SM2 回退分支）。
- 部署要求随代码注释写明：SM2 目录需包含 sm2_ca.crt + sm2_host.crt + sm2_host.key 三件套。

## 测试决策

- 先写失败用例（SM2 当前实现返回 host.* 路径且找不到子目录文件）再实现（TDD）。
- 回归范围：libs/tests C 测试 + rdbcomm 握手会话测试。

## 验收标准

- [ ] AC-1: 单测证明 SM4 算法下 build_client_profile 返回 cert_dir/<ca_cn>/sm2_ca.crt、sm2_host.crt、sm2_host.key
- [ ] AC-2: 单测证明临时目录仅含 sm2_* 三件套时 tls_cert_init_client(SM4) 成功
- [ ] AC-3: 单测证明 ED25519 路径构建与回退行为与改动前完全一致（既有断言零修改通过）
- [ ] AC-4: libs/tests 与 rdbcomm 既有回归全部保持通过
- [ ] AC-5: sec_tls_client_cert_paths 与 Go 侧布局一致性完成处置（同步修改或有据可查的差异记录）

## 范围外

- 服务端布局、CRL 命名、其他算法扩展
- 存量 host.* 目录的自动迁移

## 备注

- 来源：T0387 遗留转正式需求；现网证据：/opt/aio/cfg/certs/MySM2RootCA/ 已按 sm2_host.* 就位。
- 终审用户原话留存："ca 获取没有处理，客户端只能从 /opt/aio/cfg/certs/xxxxx/ 获取 ca"；"SM2 仅前缀"。
