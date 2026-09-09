---
schema: pdca.asset/v1
id: ontology:concept/nbu-data-encryption
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-07
dcterms_modified: 2026-09-07
owl_versionIRI: http://pdca.local/ontology/nbu-data-encryption/1.0.0
summary: NBU三链数据加密模型（客户端/磁带/磁盘-KMS），AES底座无国密，GCM多Tag规则
relations:
  specializes:
  - ontology:concept/pdca-task
  relates_to:
  - ontology:concept/cipher-mode-gcm
  - ontology:concept/cipher-mode-cfb
  - ontology:concept/cipher-mode-cbc
attributes:
- name: three_chains
  desc: NBU三条落盘链与一套管钥面的组成与证据锚定
  constraint: 须含链A客户端/链B磁带/链C磁盘-KMS与管钥面四要素及二进制函数名
  testable_signal: "运行 grep -q 'manage_drive_encryption' ontology/concept/nbu-data-encryption.md && grep -q 'mangle_aes_256_gcm' ontology/concept/nbu-data-encryption.md && grep -q 'kmsGetKeyAndKad' ontology/concept/nbu-data-encryption.md"
- name: multi_tag_rule
  desc: GCM每次调用独立12B随机IV与16B Tag，多块多组规则
  constraint: 须含malloc 0xc/0x10与重备必变的因果
  testable_signal: "运行 grep -q '0xc' ontology/concept/nbu-data-encryption.md && grep -q '0x10' ontology/concept/nbu-data-encryption.md && grep -q '重备必变' ontology/concept/nbu-data-encryption.md"
---

# NBU数据加密模型

NBU（NetBackup 10.3.0.1）数据加密 = 自带 `OpenSSL 1.1.0-fips-dev`（`NB_101_*`）底座 + 三链落盘 + KMS 管钥，无国密。

## 三链

- **链A客户端**：`bpkeyutil` 口令双哈希派生 32B（`gen_32byte_digest` 两次 `getBinaryHash`）→ 两步 `Init` 装 key/IV（`gen_init_encryption`）→ `gen_do_encryption`（`Update+Final`）→ `bpbkar EncryptBlock`（遗留 `vdes_cbc_encrypt`）→ 备份像 `.EnCrYpTiOn` 标记 + 密文。
- **链B磁带**：`bptm manage_drive_encryption/get_encryption_key` 按 `ENCR` 卷池经 `libkmsSH kmsGetKeyAndKad(ByKeyTag)/kmsGetKeysByKad` 取键 → `kmsDecryptKey/kmsTransformKey` → 驱动器硬件加密（`DRIVE_ENCRYPTION_ACTIVE`），无键冻结（`FREEZING ENCR pool`）。
- **链C磁盘/MSDP/云**：`bpdm clientEncrypt/isEncrypted/kmsKeyTag` 调 `mangle_aes_256_gcm_encrypt_with_rand_iv/decrypt`，`nbcryptocmd` 走 `GCMCrypter + KMIP`。
- **管钥面**：`nbkmscmd` 组→键→凭证三级（HMK 护 KPK），`nbckmsutil` 管云。

## 多Tag规则

`mangle` 每次调用 `malloc(0xc)` 分配 12B IV 并 `mangleGetRandom` 随机填充，`malloc(0x10)` 分配 16B Tag 并 `CTRL` 取出；解密按块设期望 Tag 并 `Final` 验签。备份按块多次调用则多组 `(IV,Tag)` 落盘，同一明文重备因 IV 随机必然密文与 Tag 不同，不存在全局单 Tag。

Source: T2071 research-report-v4.md + records/T2071-0907-nbu-data-encrypt/evidence/21-tag-iv-asm.txt
