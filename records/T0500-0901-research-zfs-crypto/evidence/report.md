# OpenZFS 加解密实现调研报告

> 任务：T0500-0901-research-zfs-crypto | 仓库：/home/black/Documents/zfs | 版本：SPA_VERSION 5000 + encryption feature | SM4-GCM 补丁 0001-icp-add-SM4-GCM-encryption-suite.patch

---

## 1. 调研目标与方法

对 OpenZFS（Linux/FreeBSD，双平台）加解密体系做源码级调研，覆盖算法、密钥、数据路径、磁盘格式、完整性与平台适配。起点为 `include/sys/fs/zfs.h:1959` 的 `zio_encrypt` 枚举，追踪至 `include/sys/zio_crypt.h`、`include/sys/dsl_crypt.h`、`module/zfs/dsl_crypt.c`、`module/os/linux/zfs/zio_crypt.c`、`module/icp/**`、`lib/libzfs/libzfs_crypto.c`、`module/zcommon/zfs_prop.c` 及 SM4 补丁 16 文件。

---

## 2. 加密算法套件与参数（AC-1）

### 2.1 ZIO 套件枚举

`include/sys/fs/zfs.h:1959-1967`
```
ZIO_CRYPT_INHERIT=0, ZIO_CRYPT_ON=1, ZIO_CRYPT_OFF=2,
ZIO_CRYPT_AES_128_CCM/192_CCM/256_CCM (3-5),
ZIO_CRYPT_AES_128_GCM/192_GCM/256_GCM (6-8),
ZIO_CRYPT_SM4_GCM=9, ZIO_CRYPT_FUNCTIONS=10
```
`ZIO_CRYPT_ON_VALUE=AES_256_GCM`（`zfs.h:1965`），`DEFAULT=OFF`。SM4 仅 GCM，无 CCM。

### 2.2 zio_crypt_table

`module/os/linux/zfs/zio_crypt.c:198-209`（FreeBSD 同构于 `module/os/freebsd/zfs/zio_crypt.c:207`）：
```
{"", ZC_TYPE_NONE, 0, "inherit"},
{"", ZC_TYPE_NONE, 0, "on"},
{"", ZC_TYPE_NONE, 0, "off"},
{SUN_CKM_AES_CCM, ZC_TYPE_CCM, 16, "aes-128-ccm"},
{SUN_CKM_AES_CCM, ZC_TYPE_CCM, 24, "aes-192-ccm"},
{SUN_CKM_AES_CCM, ZC_TYPE_CCM, 32, "aes-256-ccm"},
{SUN_CKM_AES_GCM, ZC_TYPE_GCM, 16, "aes-128-gcm"},
{SUN_CKM_AES_GCM, ZC_TYPE_GCM, 24, "aes-192-gcm"},
{SUN_CKM_AES_GCM, ZC_TYPE_GCM, 32, "aes-256-gcm"},
{SUN_CKM_SM4_GCM, ZC_TYPE_GCM, 16, "sm4-gcm"}
```
`include/sys/zio_crypt.h:53-72` 定义 `zio_crypt_info_t {ci_mechname, ci_crypt_type, ci_keylen, ci_name}`。

| 套件 | 类型 | keylen | IV | MAC | salt |
|------|------|--------|----|-----|------|
| aes-128/192/256-ccm | CCM | 16/24/32 | 12 | 16 | 8 |
| aes-128/192/256-gcm | GCM | 16/24/32 | 12 | 16 | 8 |
| sm4-gcm | GCM | 16 | 12 | 16 | 8 |

IV/SALT/MAC 长度见 `include/sys/zio.h:128-130`：`ZIO_DATA_IV_LEN=12, ZIO_DATA_SALT_LEN=8, ZIO_DATA_MAC_LEN=16, ZIO_OBJSET_MAC_LEN=32`。

### 2.3 ICP/KCF

`include/sys/crypto/common.h:84-86` 定义 `SUN_CKM_AES_CCM/AES_GCM/SM4_GCM`；FreeBSD 镜像于 `include/os/freebsd/zfs/sys/freebsd_crypto.h:41-44`。
`module/icp/illumos-crypto.c` 注册 `aes_mod_init / sm4_mod_init`；`module/icp/io/sm4.c:79-88` 注册 `SM4 Software Provider` 仅支持 `SUN_CKM_SM4_GCM`。
`module/icp/algs/sm4/sm4_impl.c:156-261` 实现 SM4 128-bit 32轮 Feistel（S-box + L/L' 线性变换）；`module/icp/algs/modes/gcm.c` 与 `ccm.c` 提供 AEAD 框架（CK params 封装、CTR+GHASH/CBC-MAC）。

### 2.4 CCM vs GCM

- CCM：CBC-MAC，需预知 `ulDataSize` 含 MAC；`module/icp/algs/modes/ccm.c`。
- GCM：CTR+GHASH，支持流式 AAD；`gcm_mode_encrypt_contiguous_blocks:86` 用低32位计数器，12字节 IV 快速构造 J0=`IV||0^31||1`，否则 GHASH 非12路径（`gcm.c:484-530`）。

---

## 3. 密钥管理与生命周期（AC-2）

### 3.1 分层

| 层 | 常量/结构 | 长度 | 生成 | 存储 |
|----|-----------|------|------|------|
| wrapping key | `WRAPPING_KEY_LEN=32` `include/sys/zio_crypt.h:38` | 32 | passphrase→PBKDF2-HMAC-SHA512 或 raw/hex 直接 | 内存 `spa_keystore.sk_wkeys`，用户 `zfs load-key` 注入 |
| master key | `zk_master_keydata[32]` | ci_keylen(16/24/32, SM4=16) | `random_get_bytes` `zio_crypt.c:260` | 加密存 `DSL_CRYPTO_MASTER_KEY_1` ZAP |
| hmac key | `zk_hmac_keydata[64]` | 64 | 同 master 随机 | 同主密钥加密存 `DSL_CRYPTO_HMAC_KEY_1` |
| current key | `zk_current_keydata[32]` | ci_keylen | HKDF-SHA512(master, salt) `zio_crypt.c:273` | 内存 `crypto_key_t + ctx_template` |

> wrapping/master 解耦：轮换口令无须重加密数据。

### 3.2 PBKDF2/HKDF

- PBKDF2 仅 `keyformat=passphrase`：`dsl_crypt.c:1404-1891` 校验 `pbkdf2salt(64bit)`/`pbkdf2iters(默认350k≥100k, zfs.h:580)`；用户态 `lib/libzfs/libzfs_crypto.c` 用 OpenSSL PBKDF2 派生32B wrapping key；内核 `hkdf_sha512` 见 `include/sys/hkdf.h:26`。
- HKDF：`zio_crypt_key_init:273` / `zio_crypt_key_change_salt:333` 调用 `hkdf_sha512(master, salt8B)` 得 current key；每400M块自动轮换 salt（`ZFS_KEY_MAX_SALT_USES_DEFAULT=400000000` `zio_crypt.c:187`）。

### 3.3 spa_keystore

`include/sys/dsl_crypt.h:148-166`：
```
spa_keystore {
  sk_dsl_keys: AVL<dsl_crypto_key_t> (dck_obj索引)
  sk_key_mappings: AVL<dsl_key_mapping_t> (km_dsobj→km_key, zio层快速查)
  sk_wkeys: AVL<dsl_wrapping_key_t> (wk_ddobj索引, refcounted)
}
dsl_wrapping_key_t {wk_keyformat, wk_salt, wk_iters, wk_key, wk_refcnt, wk_ddobj}:49-70
dsl_crypto_key_t {dck_key(zio_crypt_key_t), dck_wkey*, dck_obj, dck_holds}:111-126
dsl_key_mapping_t {km_dsobj, km_key*, km_refcnt}:133-145
```
三树职责见 `dsl_crypt.c:46-62` 注释。

### 3.4 dsl_crypto_params & 生命周期

`dsl_crypto_params_t:92-104` {`cp_cmd, cp_crypt, cp_keylocation, cp_wkey`}，`cp_cmd` 含 `NONE/RAW_RECV/NEW_KEY/INHERIT/FORCE_*`。

| 操作 | 入口 |
|------|------|
| 创建 | `dsl_crypto_params_create_nvlist` → `dmu_objset_create_crypt_check` → `dsl_dataset_create_crypt_sync`，校验 `SPA_FEATURE_ENCRYPTION`(`spa.c:6523`) |
| load-key | `spa_keystore_load_wkey`→`load_wkey_impl:181`，用户 `zfs load-key` 读file/https/prompt → `dsl_wrapping_key_create`→AVL插入→unwrap 或新建 |
| unload-key | `spa_keystore_unload_wkey`，仅无持有者可卸；`dsl_wrapping_key_free:98-108` memset清零 |
| change-key | `spa_keystore_change_key`，支持 NEW_KEY/INHERIT |
| clone/promote/rename | `dsl_crypto_key_clone_sync / dsl_dir_rename_crypt_check / promote_crypt_check:204-207` |

### 3.5 磁盘 DSL Crypto Key ZAP

`dsl_crypt.h:35-43`：每加密根在 MOS 的 ZAP 对象：
```
DSL_CRYPTO_SUITE, DSL_CRYPTO_GUID, DSL_CRYPTO_IV(12B), DSL_CRYPTO_MAC(16B),
DSL_CRYPTO_MASTER_KEY_1(ci_keylen), DSL_CRYPTO_HMAC_KEY_1(64B),
DSL_CRYPTO_ROOT_DDOBJ, DSL_CRYPTO_REFCOUNT, DSL_CRYPTO_VERSION=1
+ ZFS_PROP_KEYFORMAT/PBKDF2_SALT/ITERS
```
master/hmac 经 `zio_crypt_key_wrap:490-556` 用 AES-256-CCM + 随机IV + AAD(guid||crypt||version) 加密。

---

## 4. 数据路径与调用链（AC-3）

### 4.1 总览

```
dmu_write/arc_write → zio_write → zio_encrypt → spa_do_crypt_abd(B_TRUE)
                                          → zio_do_crypt_data/abd → zio_do_crypt_uio → crypto_encrypt
dmu_read/arc_read → zio_read → zio_decrypt → spa_do_crypt_abd(B_FALSE) → crypto_decrypt → ECKSUM on fail
```
关键调用点 `module/zfs/zio.c:597-5085`。

### 4.2 参数生成

- salt：`zio_crypt_key_get_salt:361-384` 读 `zk_salt` 并 `atomic_inc_64(zk_salt_count)`，达400M时 `hkdf` 新派生。
- IV：`zio_crypt_generate_iv:662-676`（`random_get_pseudo_bytes`）非dedup；dedup用 `zio_crypt_generate_iv_salt_dedup:724-740` 以 `HMAC_SHA512(plaintext)[0:8]→salt, [8:20]→iv` 实现同明文同密文（注释 `zio_crypt.c:147-163` 说明安全性折衷）。
- MAC：`crypto_encrypt` 输出16B，存 `cuio` 末 iovec。

编码至 blkptr：`zio_crypt_encode_params_bp:751-807`（DVA[2].dva_word[0]=salt, [1]=iv低64, blk_fill高32=iv高32；byteswap 对称）。

### 4.3 zio_do_crypt_uio

`zio_crypt.c:393-487`：依表构造 `CK_AES_CCM_PARAMS` 或 `CK_AES_GCM_PARAMS`（ivLen12/tag128），`CRYPTO_DATA_UIO` 散列 UIO，`crypto_encrypt/decrypt` 调 KCF，失败转 `EIO/ECKSUM`。

### 4.4 特殊对象

- ZIL：`zio_crypt_init_uios_zil:1403-1610`，MAC 存 `zil_chain_t.zc_eck.zec_cksum[2..3]`（`encode_mac_zil:856`），`lr_write_t.lr_blkptr` 与 chain 头明文作 AAD，其余负载加密。
- DNODE：`zio_crypt_init_uios_dnode:1615+`，核心64B明文，bonus 若 `DMU_OT_IS_ENCRYPTED` 则加密；`zio_crypt_copy_dnode_bonus:887-910` 仅拷贝加密 bonus。

### 4.5 ABD

`zio_do_crypt_abd:155-159` → `abd_iter` 构 UIO，零拷贝。

---

## 5. On-disk格式与属性接口（AC-4）

### 5.1 blkptr

```
blkptr(128B): DVA[2].dva_word[0]=salt, [1]=iv0-7, blk_fill高32=iv8-11
blk_cksum[2..3]=MAC(16B), [0..1]=密文截断校验
blk_prop: encrypt位等
```
`encode/decode_params/mac_bp:751-854` 处理端序；`BP_IS_ENCRYPTED/USES_CRYPT/IS_PROTECTED/SHOULD_BYTESWAP` 见 `include/sys/blkptr.h`。

### 5.2 属性

`include/sys/fs/zfs.h:182-192` 与 `module/zcommon/zfs_prop.c:562-684`：
- `encryption(182)` index: `off/on/aes-*-ccm/gcm/sm4-gcm/inherit`；`keyformat(184)` `none/raw/hex/passphrase`；`keylocation(183)` `prompt/file:// https://`；`pbkdf2salt(185)` hidden；`pbkdf2iters(186)` 350k≥100k；`encryptionroot(187)` 只读；`keystatus(189)` `none/unavailable/available`；`key_guid/ivset_guid` hidden。
- 约束 `zfs_prop_valid_keylocation / encryption_key_param:1006-1026`。

### 5.3 用户命令

- `zfs create -o encryption=... -o keyformat=... -o keylocation=... -o pbkdf2iters=...`
- `zfs load-key [-a|-r] [-L keylocation] <ds>` / `unload-key`
- `zfs change-key [-l|-i|-o keylocation] [-o pbkdf2iters] <ds>`
- `zfs get encryption,keystatus,encryptionroot,...`
- `zfs send -w/--raw` 原始发送，`DRR_BEGIN` 带 portable_mac，接收 `dsl_crypto_recv_raw_key_check/sync:194-201` 重建 ZAP。

### 5.4 Feature

`include/zfeature_common.h:63 SPA_FEATURE_ENCRYPTION`，池首次创建加密数据集后永久激活；`spa.c:6523-6612` 自动启用/校验。

---

## 6. 校验与完整性（AC-5）

### 6.1 三级 MAC

| 层 | 数据 | 算法 | 位置 |
|----|------|------|------|
| L0 | 用户数据 | AEAD tag 16B | blk_cksum[2..3]/ZIL内联 |
| L1+ | 下层 `blkptr_auth_buf{blk_prop,mac,pad}` SHA512截断16B | `SHA512` `zio_crypt_do_indirect_mac_checksum:1328-1379` | 上层 ck[2..3] |
| objset | `os_type/os_flags/metadnode/spill/userused/groupused/projectused` | HMAC-SHA512截32B `zio_crypt_do_objset_hmacs:1137-1312` | objset_phys尾双MAC portable/local |

`zio_crypt_bp_zero_nonportable_blkprop:916-968` 清 compress/psize 等不可移植位（L0外）。

### 6.2 失败语义

- `crypto_decrypt→CRYPTO_INVALID_MAC → ECKSUM`（`zio_do_crypt_uio:477`）
- 间接校验同 `ECKSUM`（`1338-1352`）
- `blk_cksum[0..1]` 明文校验可在无密钥时 scrub 检静默损坏。

### 6.3 流程

写入：`zio_write→zio_encrypt_data→encode→checksum(compress→encrypt→checksum)`；读取：`zio_read→zio_decrypt_data→decode→crypto_decrypt→ECKSUM处理`（`zio.c:4987-5085`）。

---

## 7. SM4-GCM扩展及平台适配（AC-6）

### 7.1 补丁清单

`0001-icp-add-SM4-GCM...patch` 16文件 +810/-58：
- `zfs.h:1964` 新增 `ZIO_CRYPT_SM4_GCM`
- `common.h:86` / `freebsd_crypto.h:44` 新增 `SUN_CKM_SM4_GCM`
- `sm4_impl.c:268` / `sm4_impl.h:80` SM4 128/32轮实现
- `io/sm4.c:359` KCF provider，仅 GCM
- `gcm.c:629-700` 重构 `gcm_init_ctx` 先判 `GCM_USE_GENERIC`
- `illumos-crypto.c:5` 注册
- `os/*/zio_crypt.c` 表项 `SM4_GCM,16,sm4-gcm`
- `qat_crypt.c:10` SM4即EOPNOTSUPP回退
- `crypto_os.c:13` / `zio_crypt.c:11` FreeBSD 追加
- `zfs_prop.c:3` description追加 `sm4-gcm`
- `Makefile.am/Kbuild.in` 编译

### 7.2 细节

- GB/T 32907-2016，128-bit块/钥匙32轮，S-box256项，复用 `aes_copy/xor_block` 与 `gcm_mode_*`，密钥调度 `K[36]` 修正越界。
- Wrapping 固定 AES-256-CCM（SM4仅16B，避免安全性降级）。

### 7.3 QAT/GCM适配

- `qat_crypt.c:170-174` SM4直接 `EOPNOTSUPP` 软回退，避免误用 AES-GCM。
- `sm4.c:188-192` 强制 `GCM_USE_GENERIC`；`gcm.c:632` SM4走 `GCM_IMPL_GENERIC`，禁用 AVX 的 `pclmulqdq/vpclmulqdq` 表（依赖 `aes_key_t` 布局）。

### 7.4 影响

仅新增套件，不改老格式；`zfs get encryption` 新增 `sm4-gcm`；测试 `zfs-tests` 尚未覆盖 SM4，需扩展。

---

## 8. 子系统集成

| 子系统 | 文件 | 作用 |
|--------|------|------|
| ARC | `arc.c:1335,1869,1936` | `arc_hdr_decrypt/fill_hdr_crypt` 查 `spa_keystore_lookup_key` 并 `spa_do_crypt_abd`；`b_crypt_hdr` 存参数 |
| DMU | `dmu_objset.c/dmu_recv.c` | `os_flags` 含 accounting 影响 local MAC；recv分check/sync |
| ZIO | `zio.c` | 调度加密/校验，`dio_checksum/mac` 顺序 |
| SPA | `spa.c:6523` | `spa_create_check_encryption_params` 强依赖feature |
| QAT | `qat_crypt.c` | 硬件offload失败回ICP |
| libzfs | `libzfs_crypto.c` | 用户态 PBKDF2与错误映射 |

---

## 9. 建议

1. wrapping/master `memset`清零已覆盖，续审所有 `ck_data` 释放点。
2. salt 400M≈1.6PB(4K块)，高吞吐可收紧 `zfs_key_max_salt_uses:190`。
3. PBKDF2默认350k约200ms，建议500k+并 `change-key` 同步ZAP。
4. SM4 测试缺口：需国密向量（GB/T附录A）+ `zfs-tests` 新增sm4-gcm创建/读写/scrub/raw send回归。
5. 未来硬件SM4应新增独立套件而非复用GCM provider。

---

## 10. 验收映射

| AC | 章节 | 锚点 |
|----|------|------|
| AC-1 | §2 | `zfs.h:1959`, `zio_crypt.c:198`, `common.h:86` |
| AC-2 | §3 | `dsl_crypt.h:48-166`, `dsl_crypt.c:46-62`, `zio_crypt.c:187-676` |
| AC-3 | §4 | `zio_crypt.c:393-1610`, `zio.c:597-5085`, `arc.c:1869` |
| AC-4 | §5 | `zio.h:128-130`, `zfs_prop.c:562-684`, `dsl_crypt.h:35-43` |
| AC-5 | §6 | `zio_crypt.c:856-1394`, `gcm.c` |
| AC-6 | §7 | 补丁全量 + `sm4_impl.c:25-261`, `io/sm4.c` |
| AC-7 | 本章 | 本报告 + manifest + convergence-map |

*生成于 2026-09-01，基于当前工作树+SM4补丁。*

## 附录 A：索引

```
zfs.h:1959 ZIO_CRYPT
zio_crypt.h:38-161 WRAPPING/MASTER与zk
dsl_crypt.h:35-229 ZAP键+三树
zio.h:128 IV/SALT/MAC
zio_crypt.c 1962行 全量
dsl_crypt.c 2922行 三树+PBKDF2
sm4_impl.c SM4轮
sm4.c provider
gcm.c GCM
zfs_prop.c:228,567 sm4-gcm值
libzfs_crypto.c 用户态
0001...patch 16files+810
```

## 附录 B：缩略语

- AEAD, KCF, ICP, ABD, ZAP, HKDF, PBKDF2, GHASH, CCM/GCM
