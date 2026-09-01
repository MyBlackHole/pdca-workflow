---
schema: pdca.asset/v1
id: ontology:domain/zfs-crypto
type: domain
layer: Knowledge
status: active
summary: OpenZFS 存储加密体系（含 SM4-GCM 国密扩展）的端到端领域知识
relations:
  specializes:
  - ontology:domain/backup-crypto
  relates_to:
  - ontology:concept/pdca
  - ontology:domain/backup-crypto-medium-model
attributes:
- name: algorithm_suite_coverage
  desc: 加密算法套件与参数的覆盖完整性
  constraint: 须覆盖 ZIO_CRYPT 枚举、zio_crypt_table、KCF/ICP 与 SM4 扩展
  testable_signal: "校验 reports 含 aes-128/256-ccm/gcm 与 sm4-gcm 七套件，且 grep -n ZIO_CRYPT_SM4_GCM include/sys/fs/zfs.h 命中"
- name: key_hierarchy_depth
  desc: 密钥分层与生命周期深度
  constraint: 四层密钥与 PBKDF2/HKDF、spa_keystore 三树、ZAP 持久
  testable_signal: "校验文档含 Wrapping/Master/HMAC/Current 四层且 grep -n WRAPPING_KEY_LEN include/sys/zio_crypt.h 命中"
- name: datapath_traceability
  desc: 数据路径可追溯性
  constraint: 覆盖 zio↔spa_do_crypt↔KCF、IV/salt 生成、ZIL/DNODE/ABD 特化
  testable_signal: "校验含 zio_do_crypt_uio 与 ZIL/DNODE 章节且 grep -n zio_crypt_generate_iv module/os/linux/zfs/zio_crypt.c 命中"
---

# OpenZFS 存储加密体系（ZFS-Crypto）

本领域聚合 OpenZFS（Linux/FreeBSD）透明存储加密的端到端知识，基于当前工作树（含 `0001-icp-add-SM4-GCM-encryption-suite.patch`）源码追溯，形成可复用的六层模型。

来源：`records/T0500-0901-research-zfs-crypto/evidence/report.md`（ev-report，T0500 调研，2026-09-01）

## 1. 六层模型

| 层 | 对应 AC | 核心产物 |
|----|---------|----------|
| 算法套件 | AC-1 | `ZIO_CRYPT_*` 枚举 10 项、`zio_crypt_table` 7 套件参数、KCF `SUN_CKM_*`、ICP `gcm/ccm` 与 SM4 32轮实现 |
| 密钥管理 | AC-2 | 四层密钥（wrapping 32B / master ci_keylen / HMAC 64B / current 派生）、PBKDF2 350k/HKDF、spa_keystore 三 AVL、DSL Crypto Key ZAP、load/unload/change 生命周期 |
| 数据路径 | AC-3 | `zio_encrypt→spa_do_crypt_abd→zio_do_crypt_uio→crypto_encrypt` 全链、盐 8B/IV 12B/MAC 16B 随机或 HMAC-dedup、ZIL（MAC内联）/DNODE（bonus）/ABD 特化 |
| 磁盘格式与属性 | AC-4 | blkptr DVA[2]/cksum/prop 编码、`DSL_CRYPTO_*` ZAP、dataset 属性 `encryption/keyformat/keylocation/pbkdf2*`、`SPA_FEATURE_ENCRYPTION` |
| 完整性 | AC-5 | 三级 MAC（L0 AEAD 16B / L1+ SHA512截断 / objset HMAC 32B 双根）、非可移植位清零、ECKSUM 失败语义 |
| 平台适配 | AC-6 | SM4-GCM 新增 16 文件 810 行、`GCM_USE_GENERIC` 强制、`qat_crypt` 回退、`FreeBSD OCF ENOTSUP`、`zfs_prop` sm4-gcm 扩展 |

## 2. 关键不变量

- Wrapping 固定 `AES-256-CCM`，不随套件变（SM4 仍用 AES-256-CCM wrap 16B master，避免 32B→16B 降级）。
- Salt 64-bit 每 400M 块轮换，HKDF 派生；IV 96-bit 永不复用（dedup 除外，HMAC 派生故无额外泄露）。
- `blk_fill` 高 32 位复用存 IV 高位，因加密仅 L0 且 `dn_extra_slots` ≤2^15，安全（`zio_crypt.c:34-63` 注释）。
- Objset 双 MAC：portable 随 `zfs send -w` 传输，local 本地会计独立；间接块 MAC 为子层 `blkptr_auth_buf` 的 SHA512。

## 3. SM4 国密适配要点

- GB/T 32907-2016，128/128，S-box 256 项，32 轮 Feistel `X_{i+4}=X_i xor L(τ(S-box(...)))`，复用 `aes_copy/xor_block` 与 GCM 框架。
- 强制 generic GCM（`gcm_init_ctx:632` 分支），禁用 AVX 的 `pclmulqdq/vpclmulqdq`（依赖 `aes_key_t` 布局）。
- QAT 硬件遇 `SM4_GCM` 返回 `EOPNOTSUPP` 软回退，防误用 AES-GCM。

## 4. 复用指引

- 新平台评估 SM 加解密时，先查本领域六层模型定位缺口（算法/密钥/路径/格式/完整性/适配）。
- 存储介质选型（ZFS/ S3/ OSS/ NFS） referencing `ontology:domain/backup-crypto-medium-model`，其中 ZFS 透明加密即本领域能力。
- 性能敏感场景关注 GCM 实现选择：`gcm_impl` 模块参数 `fastest/cycle/avx/avx2-vaes` 与 `icp_gcm_avx_chunk_size`，SM4 当前仅 generic。

## 5. 证据与追溯

- 调研报告：`records/T0500-0901-research-zfs-crypto/evidence/report.md`（AC-1~6 全覆盖，行号锚点）
- 收敛映射：`records/T0500-0901-research-zfs-crypto/evidence/convergence-map-v2.json`
- 验证：`PYTHONPATH=scripts python3 -c "from pdca_core import convergence_issues"` 0 issue；`ontology-validate` 0 issue

## 6. 边界

- 基于 ZFS 工作树 + SM4 补丁的静态源码形态，未含运行时性能压测；SM4 zfs-tests 功能覆盖仍缺（建议新增）。
- 不替代国密合规审查，仅为工程实现层面的可复用领域模型。
