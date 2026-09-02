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
  testable_signal: "运行 grep -q 'zio_crypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md 且 grep -q 'ZIO_CRYPT_SM4_GCM' include/sys/fs/zfs.h 命中且 grep -q 'zio_crypt_table' module/os/linux/zfs/zio_crypt.c 命中"
- name: key_hierarchy_depth
  desc: 密钥分层与生命周期深度
  constraint: 四层密钥与 PBKDF2/HKDF、spa_keystore 三树、ZAP 持久
  testable_signal: "运行 grep -q 'zio_crypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md 且 grep -q 'WRAPPING_KEY_LEN' include/sys/zio_crypt.h 命中"
- name: datapath_traceability
  desc: 数据路径可追溯性
  constraint: 覆盖 zio↔spa_do_crypt↔KCF、IV/salt 生成、ZIL/DNODE/ABD 特化
  testable_signal: "运行 grep -q 'zio_crypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md 且 grep -q 'zio_do_crypt_uio' module/os/linux/zfs/zio_crypt.c 命中且 grep -q 'zio_crypt_generate_iv' module/os/linux/zfs/zio_crypt.c 命中"
- name: transform_encrypt_branch
  desc: ZIO transform 栈 encrypt 分支与 abd 替换可测，对应 ZIO_STAGE_ENCRYPT(1<<6) 的压栈-弹栈及 IV/salt 生成与 ZIO pipeline 协同
  constraint: 覆盖 ZIO_STAGE_ENCRYPT(1<<6) 在 ZIO_WRITE_PIPELINE(WRITE_COMPRESS后、CHECKSUM_GENERATE前) 的位置与 zio_pipeline[6]=zio_encrypt、zio_encrypt(zio.c:4953) 七分支（GANG/非allocating/非encrypted/RAW/L>0/OBJSET/!ENCRYPTED/主加密）与 zio_decrypt(zio.c:571) 回调、zio_push_transform/zio_pop_transforms(502)的 zt_orig_abd/zt_bufsize/zt_transform 链与 abd 替换（eabd psize/NULL）、zio_read_bp_init(1806)的 PROTECTED→push(zio_decrypt) 读侧压栈、spa_do_crypt_abd(2826)的 salt/IV 双分支（!dedup→get_salt+generate_iv 随机 / dedup→generate_iv_salt_dedup HMAC确定性 / ZIL已生成）、zio_crypt_key_get_salt(361)的 atomic_inc_64 + 400M→hkdf 轮换、zio_crypt_table[ZIO_CRYPT_FUNCTIONS](198)的 7套件(aes-128/192/256-ccm/gcm + sm4-gcm) 与 ZC_TYPE_CCM/GCM、zio_do_crypt_uio(394)的 CCM/GCM 参数分支与 crypto_encrypt/decrypt(ECKSUM)、ZIL(zio_crypt_init_uios_zil:1403)的 zil_chain_t.zc_eck 与 DNODE(zio_crypt_init_uios_dnode:1615)的 bonus 特化及 no_crypt 短路，经 C4 L3 与时序/状态机可一图建模
  testable_signal: "运行 grep -q 'zio_crypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md 且 grep -q 'ZIO_STAGE_ENCRYPT' include/sys/zio_impl.h 命中且 grep -q 'zio_encrypt' module/zfs/zio.c 命中且 grep -q 'zio_decrypt' module/zfs/zio.c 命中且 grep -q 'zio_push_transform' module/zfs/zio.c 命中"
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

## 5. Encrypt-Transform 分支 — ZIO transform 栈协同（T0524 深化）

加密分支以 `zio_crypt_table[ZIO_CRYPT_FUNCTIONS]`（`module/os/linux/zfs/zio_crypt.c:198`）表驱动，每项 `zio_crypt_info_t`（`include/sys/zio_crypt.h:53`）含 `ci_mechname`（`SUN_CKM_AES_CCM/AES_GCM/SM4_GCM`，`include/sys/crypto/common.h:84`）、`ci_crypt_type`（`ZC_TYPE_CCM/GCM`，`zio_crypt.h:46`）与 `ci_keylen`（`16/24/32`）。`enum zio_encrypt`（`include/sys/fs/zfs.h:1954`）10 项：`INHERIT/ON/OFF/AES_128/192/256_CCM/AES_128/192/256_GCM/SM4_GCM`，`ON_VALUE=AES_256_GCM`（`zfs.h:1968`），`SM4_GCM` 仅 `GCM+16B`。`ZIO_STAGE_ENCRYPT=1<<6`（`zio_impl.h:137`）在 `ZIO_WRITE_PIPELINE`（`zio_impl.h:224`）中位列 `WRITE_COMPRESS(1<<5)` 之后、`CHECKSUM_GENERATE(1<<7)` 之前；`zio_pipeline[6]=zio_encrypt`（`zio.c:5807`）。

写侧 `zio_encrypt`（`zio.c:4953`）七分支：`1) io_child_type==GANG→return（根已加密） 2) !IO_IS_ALLOCATING且ot!=ZIL→return（仅ZIL可重写） 3) !zp_encrypt且!BP_IS_ENCRYPTED→SET_CRYPT false→return 4) RAW_ENCRYPT→encode_mac/params+byteswap push(NULL)→return 5) L>0→indirect cksum→encode_mac→return 6) ot==OBJSET→objset双HMAC→return 7) !DMU_OT_IS_ENCRYPTED(ot)→仅HMAC→encode_mac→return；主路径 `alloc enc_buf/eabd(abd_get_from_buf)` → `spa_do_crypt_abd(B_TRUE, salt, iv, mac, psize, io_abd, eabd)`（`dsl_crypt.c:2826` 中 `lookup_key→!dedup?get_salt+generate_iv : generate_iv_salt_dedup`）→ `ZIL? decode_params→encode_mac_zil+push(eabd, psize, psize, NULL) : encode_params_bp+encode_mac_bp → no_crypt?free(eabd):push(eabd, psize, psize, NULL)`（`zio.c:5081/5091` 的 `zt_orig_abd=io_abd(明文)` 链，`transform=NULL` 仅替换 `abd`）。读侧 `zio_read_bp_init`（`zio.c:1806`）在 `BP_IS_PROTECTED(bp) && !RAW_ENCRYPT && ZIO_CHILD_LOGICAL` 时 `zio_push_transform(abd_alloc_sametype(psize), psize, psize, zio_decrypt)` 压 `zio_decrypt`（`zio.c:571` 的三段：`indirect MAC cksum` / `authenticated ot→HMAC` / `正常 decode_params+decode_mac_zil/bp → spa_do_crypt_abd(B_FALSE)→ECKSUM→ereport`），`zio_pop_transforms`（`zio.c:520` 的 `while(zt) { if(transform) transform(orig); if(bufsize) abd_free(io_abd); io_abd=orig; }`）逆序还原 `abd` 与 `size`。

IV/salt 生成双分支：`spa_do_crypt_abd`（`dsl_crypt.c:2861`）中 `encrypt && ot!=ZIL && !dedup → zio_crypt_key_get_salt(361, RW_READER取zk_salt + atomic_inc_64(zk_salt_count)≥400M→zio_crypt_key_change_salt(314, hkdf_sha512新派生)) + zio_crypt_generate_iv(662, random_get_pseudo_bytes 12B)` 随机路径；`encrypt && dedup → zio_crypt_generate_iv_salt_dedup(724, zio_crypt_do_hmac(plaintext)→digest[SHA512]→salt[0:8]+iv[8:20])` 确定性路径（HMAC防明文泄露）；`ZIL` 已在 `zio_alloc_zil` 时生成。编码：`zio_crypt_encode_params_bp(752)` 的 `DVA[2].dva_word[0]=salt / [1]=iv[0:8] / BP_SET_IV2=iv[8:12]`（`blk_fill高32` 复用，安全因 `L0 fill<2^32`）与 `zio_crypt_encode_mac_bp(810)` 的 `blk_cksum.zc_word[2..3]=MAC`，均含 `BSWAP_64/32` 分支。`zio_do_crypt_uio(394)` 按 `ci_crypt_type==CCM ? CK_AES_CCM_PARAMS(ulNonceSize12/MAC16/DataSize含MAC) : CK_AES_GCM_PARAMS(ulIvLen12/TagBits128/pAAD)` 分线，经 `CRYPTO_DATA_UIO` 调 `crypto_encrypt/decrypt(ECKSUM on CRYPTO_INVALID_MAC)`，`QAT` 硬件经 `qat_crypt_use_accel→qat_crypt` 短路（`ZIL/DNODE` 不走 QAT，失败软回退）。C4 L3 与时序/状态机可一图建模该 `套件→HKDF→salt/IV双分支→ABD替换→压栈-弹栈` 全链。

Source: `openzfs/zfs/include/sys/fs/zfs.h:1954-1969`（`enum zio_encrypt` 10项）+ `openzfs/zfs/include/sys/zio_crypt.h:46-72`（`zio_crypt_info_t`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:198-209`（`zio_crypt_table`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:361-384`（`zio_crypt_key_get_salt` 的 `400M` 轮换）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:662-676`（`zio_crypt_generate_iv`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:724-740`（`zio_crypt_generate_iv_salt_dedup`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:751-854`（`encode_params/mac_bp`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:394-487`（`zio_do_crypt_uio` 的 `CCM/GCM` 分支）+ `openzfs/zfs/module/zfs/zio.c:4953-5096`（`zio_encrypt` 七分支）+ `openzfs/zfs/module/zfs/zio.c:571-702`（`zio_decrypt`）+ `openzfs/zfs/module/zfs/zio.c:502-538`（`zio_push_transform/pop`）+ `openzfs/zfs/module/zfs/zio.c:1806-1827`（`zio_read_bp_init` 的 `push(zio_decrypt)`）+ `openzfs/zfs/module/zfs/dsl_crypt.c:2826-2919`（`spa_do_crypt_abd` 双分支）

## 6. 决策树

```mermaid
flowchart TD
    START([ZIO 到达 ZIO_STAGE_ENCRYPT<br/>zio_encrypt]) --> Q0{io_child_type==GANG?}
    Q0 -- 是 --> A0[短路：根已加密<br/>return 不 push]
    Q0 -- 否 --> Q1{IO_IS_ALLOCATING<br/>或 ot==ZIL?}
    Q1 -- 否 --> A1[短路：非分配且非 ZIL<br/>不重加密 return]
    Q1 -- 是 --> Q2{zp_encrypt 或 BP_IS_ENCRYPTED?}
    Q2 -- 否 --> A2[SET_CRYPT false<br/>return 不加密]
    Q2 -- 是 --> Q3{RAW_ENCRYPT?}
    Q3 -- 是 --> A3[RAW 路径<br/>encode_mac_bp(zp_mac)<br/>encode_params_bp(zp_salt/iv)<br/>byteswap DNODE push NULL→return]
    Q3 -- 否 --> Q4{L>0 间接块?}
    Q4 -- 是 --> A4[indirect cksum<br/>SHA512 MACs→encode_mac_bp<br/>SET_CRYPT→return]
    Q4 -- 否 --> Q5{ot==OBJSET?}
    Q5 -- 是 --> A5[OBJSET 双 HMAC<br/>portable/local SHA512-HMAC<br/>SET_CRYPT→return]
    Q5 -- 否 --> Q6{DMU_OT_IS_ENCRYPTED(ot)?}
    Q6 -- 否 --> A6[仅认证<br/>spa_do_crypt_mac_abd HMAC<br/>→encode_mac_bp→return]
    Q6 -- 是 --> A7[分配 enc_buf/eabd<br/>zio_buf_alloc psize<br/>abd_get_from_buf]
    A7 --> Q7{ot==ZIL?}
    Q7 -- 是 --> ZIL_DECODE[decode_params_bp 已有 salt/iv<br/>取自 DVA_ALLOC 时]
    Q7 -- 否 --> SET_CRYPT[SET_CRYPT true]
    ZIL_DECODE --> CRYPT
    SET_CRYPT --> CRYPT[spa_do_crypt_abd B_TRUE<br/>salt/iv/mac + io_abd→eabd]
    CRYPT --> Q8{dedup?}
    Q8 -- 否 且非 ZIL --> RAND[get_salt<br/>atomic_inc≥400M→hkdf 轮换<br/>+ generate_iv 随机 12B]
    Q8 -- 是 dedup --> DEDUP[generate_iv_salt_dedup<br/>HMAC(plaintext)<br/>→salt[0:8]/iv[8:20] 确定性]
    Q8 -- ZIL --> ZILGEN[已生成 跳过]
    RAND --> UIO
    DEDUP --> UIO
    ZILGEN --> UIO
    UIO[zio_do_crypt_data<br/>选 current_key/hkdf临时key<br/>qat_crypt?硬件:软件<br/>init_uios ZIL/DNODE/normal<br/>→do_crypt_uio CCM/GCM→crypto_encrypt]
    UIO --> Q9{ot==ZIL?}
    Q9 -- 是 --> ZIL_ENC[encode_mac_zil enc_buf<br/>push eabd psize/NULL<br/>abd 替换]
    Q9 -- 否 --> ENC_DATA[encode_params_bp salt/iv<br/>encode_mac_bp mac<br/>DVA[2].w0=salt / w1=iv0-7<br/>blk_fill高32=iv8-11 / cksum2-3=MAC]
    ENC_DATA --> Q10{no_crypt?<br/>DNODE 无 bonus}
    Q10 -- 是 --> FREE[free eabd<br/>不压栈]
    Q10 -- 否 --> PUSH[push eabd psize/NULL<br/>io_abd=eabd 密文<br/>zt_orig_abd=明文]
    ZIL_ENC --> READY[READY→VDEV]
    FREE --> READY
    PUSH --> READY
    A0 --> READY
    A1 --> READY
    A2 --> READY
    A3 --> READY
    A4 --> READY
    A5 --> READY
    A6 --> READY
    READY --> VDEV[VDEV_IO_START→DVA_ALLOC<br/>→vdev_queue_io]

    VDEV --> READ_SIDE{读侧?}
    READ_SIDE -- 写 --> END_W([VDEV Done<br/>不弹栈 保留密文])
    READ_SIDE -- 读 zio_read_bp_init --> RPUSH{PROTECTED 且 !RAW_ENCRYPT<br/>且 LOGICAL?}
    RPUSH -- 否 --> VDEV2[VDEV 读]
    RPUSH -- 是 --> DO_PUSH[push abd_alloc_sametype psize<br/>psize/ zio_decrypt]
    DO_PUSH --> VDEV2
    VDEV2 --> VERIFY[CHECKSUM_VERIFY 密文]
    VERIFY --> POP[pop→zio_decrypt<br/>decode_params→decode_mac<br/>→spa_do_crypt_abd B_FALSE<br/>→crypto_decrypt]
    POP --> Q11{MAC 校验?}
    Q11 -- ECKSUM --> EIO[EIO + ereport<br/>非 speculative]
    Q11 -- OK --> OK2[还原至 orig_abd<br/>no_crypt?abd_copy]
    OK2 --> Q12{有 COMPRESS 栈?}
    Q12 -- 是 --> DECOMP[pop→zio_decompress<br/>psize→lsize]
    Q12 -- 否 --> DONE([Done 明文])
    DECOMP --> DONE
    EIO --> DONE
```

Source: `openzfs/zfs/module/zfs/zio.c:4953`（`zio_encrypt` 七分支）+ `openzfs/zfs/module/zfs/zio.c:571`（`zio_decrypt` 三段）+ `openzfs/zfs/module/zfs/zio.c:502`（`zio_push_transform` 的 `zt_orig_abd`）+ `openzfs/zfs/module/zfs/dsl_crypt.c:2826`（`spa_do_crypt_abd` 的 `dedup/ZIL` 分支）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:361`（`400M` 轮换）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:724`（`HMAC dedup`）+ `openzfs/zfs/include/sys/zio_impl.h:137`（`ZIO_STAGE_ENCRYPT=1<<6`）

## 7. 正例

```c
// 正例1：写 pipeline 正确含 ENCRYPT 压栈，套件选型 SM4-GCM 与 HKDF 派生正确
enum zio_encrypt crypt = ZIO_CRYPT_SM4_GCM; // zfs.h:1964 SM4 仅 GCM 16B
const zio_crypt_info_t *ci = &zio_crypt_table[crypt];
assert(ci->ci_crypt_type == ZC_TYPE_GCM && ci->ci_keylen == 16); // SM4 的 GCM/16
assert(strcmp(ci->ci_mechname, SUN_CKM_SM4_GCM) == 0); // common.h:86
// zio_crypt_key_init(SM4_GCM, key) → random guid/master/hmac/salt → hkdf(master,salt)→current
zio_crypt_key_t key; VERIFY0(zio_crypt_key_init(ZIO_CRYPT_SM4_GCM, &key));
assert(key.zk_crypt == ZIO_CRYPT_SM4_GCM && key.zk_version == 1);

// 正例2：ZIO_STAGE_ENCRYPT 在 WRITE_PIPELINE 的位置与派发表配对
assert((ZIO_WRITE_PIPELINE & ZIO_STAGE_ENCRYPT) != 0); // 1<<6 在 WRITE 中
assert((ZIO_WRITE_PIPELINE & ZIO_STAGE_WRITE_COMPRESS) != 0); // COMPRESS(1<<5)在前
assert((ZIO_WRITE_PIPELINE & ZIO_STAGE_CHECKSUM_GENERATE) != 0); // GENERATE(1<<7)在后
extern zio_pipe_stage_t *zio_pipeline[]; assert(zio_pipeline[6] == zio_encrypt); // zio.c:5807

// 正例3：非 dedup 随机 IV/salt 生成与编码正确
zio_t *zio = zio_create(pio, spa, txg, bp, abd, lsize, psize, done, NULL,
    ZIO_TYPE_WRITE, ZIO_PRIORITY_SYNC_WRITE, 0, NULL, 0, ZIO_STAGE_OPEN,
    ZIO_WRITE_PIPELINE); // 含 ENCRYPT
zio->io_prop.zp_encrypt = B_TRUE; BP_SET_TYPE(bp, DMU_OT_PLAIN_FILE_CONTENTS);
zio_execute(zio); // __zio_execute 命中 ZIO_STAGE_ENCRYPT → zio_encrypt
// 内部分支：!dedup → zio_crypt_key_get_salt(&dck->dck_key, salt) + zio_crypt_generate_iv(iv)
// salt→DVA[2].w0, iv[0:8]→w1, iv[8:12]→blk_fill高32, MAC→cksum[2..3]
// 主路径 push(eabd, psize, psize, NULL) abd 替换，io_abd 已为密文

// 正例4：dedup 确定性 IV/salt 生成与同明文同密文
uint8_t dedup_salt[8], dedup_iv[12];
zio_crypt_generate_iv_salt_dedup(&key, plainbuf, datalen, dedup_iv, dedup_salt);
// 内部 HMAC-SHA512(plaintext)→salt=[0:8], iv=[8:20]，同明文必同 salt/IV
// spa_do_crypt_abd(B_TRUE, ..., dedup=B_TRUE, ...) 走此分支，验证 dedup 去重仍有效

// 正例5：读侧 PROTECTED 压 zio_decrypt 与逆序弹栈
blkptr_t *rbp = &zio->io_bp_copy; // 已含 DVA[2]salt/iv 与 cksum MAC
// zio_read_bp_init 中：if (BP_IS_PROTECTED(rbp) && !(flags & RAW_ENCRYPT) && LOGICAL)
//     zio_push_transform(zio, abd_alloc_sametype(abd, psize), psize, psize, zio_decrypt);
// 此时 io_transform_stack 顶为 zio_decrypt，VDEV 完成后 pop 触发 zio_decrypt 回调
// zio_decrypt 内：decode_params_bp→salt/iv, decode_mac_bp→mac, spa_do_crypt_abd(B_FALSE)→明文至 orig_abd
// 若有压缩则再 pop→zio_decompress 解压

// 正例6：ZIL/DNODE 特化与 no_crypt 短路正确
// ZIL：zio_crypt_init_uios_zil 中 header+lr_write_t bp 明文，AAD 含非加密部分，MAC→zc_eck
// DNODE：zio_crypt_init_uios_dnode 中 core+blkptr 明文/AAD，bonus 加密；若无加密 bonus则 no_crypt→free(eabd)不压栈
// OBJSET：仅 HMAC 不走 AEAD，portable/local 双 MAC
```

命中：`ZIO_CRYPT_SM4_GCM` 的 `ZC_TYPE_GCM+16` 与 `SUN_CKM_SM4_GCM` 配对正确，`ZIO_WRITE_PIPELINE` 位图含 `ENCRYPT(1<<6)` 且 `zio_pipeline[6]==zio_encrypt`，`spa_do_crypt_abd` 的 `!dedup→get_salt+generate_iv` 与 `dedup→HMAC` 双分支正确，`encode_params_bp` 的 `DVA[2]+blk_fill` 与 `encode_mac_bp` 的 `cksum[2..3]` 编码正确，`zio_push_transform(NULL)` 的 `abd` 替换与 `zio_read_bp_init` 的 `push(zio_decrypt)` 读侧压栈及 `zio_pop_transforms` 逆序还原正确。

## 8. 反例

```c
// 反例1：pipeline 位图漏 ENCRYPT 导致加密数据集明文落盘
zio_t *zio = zio_create(pio, spa, txg, bp, abd, lsize, psize, done, NULL,
    ZIO_TYPE_WRITE, ZIO_PRIORITY_SYNC_WRITE, 0, NULL, 0, ZIO_STAGE_OPEN,
    ZIO_WRITE_COMMON_STAGES | ZIO_STAGE_WRITE_BP_INIT | ZIO_STAGE_WRITE_COMPRESS
    /* 漏 ZIO_STAGE_ENCRYPT */ | ZIO_STAGE_DVA_ALLOCATE); // 错：无 ENCRYPT，明文直接 DVA_ALLOC→VDEV
// 结果：BP_IS_ENCRYPTED 假，scrub 仍过但无 MAC，泄露明文且 raw send 失败

// 反例2：错将 ENCRYPT 当非栈，在 CHECKSUM_GENERATE 后手写 MAC
zio_encrypt(zio); // 已 push(eabd) 后
zio_crypt_encode_mac_bp(bp, fake_mac); // 错：在 push 后又手写 cksum[2..3]，覆盖真实 MAC→解密必 ECKSUM
// 正：仅 zio_encrypt 内 encode_mac，外部不再触 cksum

// 反例3：漏配对 pop 导致 abd 悬挂密文
zio_push_transform(zio, eabd, psize, psize, NULL); // 加密替换
// 漏 zio_pop_transforms：读完成未弹栈，abd 仍指向密文，后续 DECOMPRESS 以密文解压直接 ECKSUM/EIO
// 更隐蔽：CHECKSUM_VERIFY 失败后未重试直接上抛，漏 vs_checksum_errors 统计

// 反例4：dedup 块用随机 IV 导致去重失效且 IV 复用风险
uint8_t salt[8], iv[12]; zio_crypt_generate_iv(iv); zio_crypt_key_get_salt(key, salt);
// 错：对 dedup=true 的块走随机路径，同明文得不同 salt/IV→不同密文，dedup 比对失败且浪费空间
// 正：dedup 必走 zio_crypt_generate_iv_salt_dedup(HMAC)，保证同明文同密文

// 反例5：非 dedup 块用 HMAC 确定性 IV 泄露块相等语义
zio_crypt_generate_iv_salt_dedup(key, plainbuf, datalen, iv, salt); // 错：非 dedup 块走 HMAC
// 结果：相同明文的非 dedup 块密文相同，攻击者可判块相等（虽无 dedup 语义需求，也不应泄露）
// 正：仅 dedup 块可接受此泄露（dedup 本就泄露相等性），普通块必随机

// 反例6：ZIL 块在非 DVA_ALLOC 阶段手造 salt/IV
uint8_t zil_salt[8], zil_iv[12]; random_get_bytes(zil_salt, 8); // 错：ZIL 的 salt/IV 应在 zio_alloc_zil 时生成并 encode 至 bp
// 结果：encode_params_bp 与 ZIL header 的 zc_eck MAC 不匹配，claim 时校验失败

// 反例7：DNODE 无 bonus 时仍 push 导致空压栈
// 错：对 !DMU_OT_IS_ENCRYPTED(bonustype) 的 dnode 仍 alloc eabd 并 push，no_crypt 本应 free
// 正：zio_encrypt 中 no_crypt==B_TRUE→free(eabd) 不 push

// 反例8：混淆 CCM 与 GCM 参数导致解密 ECKSUM
CK_AES_CCM_PARAMS ccmp; ccmp.ulNonceSize = 12; // 错：对 GCM 套件填 CCM 结构
// 正：zio_do_crypt_uio 内按 ci_crypt_type 分支，CCM→CCM_PARAMS(DataSize含MAC)，GCM→GCM_PARAMS(IvLen/TagBits/AAD)

// 反例9：400M 轮换边界漏 atomic_inc 导致 salt 复用超限
// 错：直接读 zk_salt 而不经 zio_crypt_key_get_salt 的 atomic_inc_64 检查，超 400M 未轮换
// 结果：超 birthday 边界后 IV 碰撞概率>1/1e12，GCM/CCM 严禁 IV 复用→明文泄露风险
// 正：必经 get_salt 的 RW_READER + atomic_inc + ≥MAX→change_salt(hkdf)

// 反例10：byteswap 分支遗漏导致跨端解密失败
// 错：始终 encode_params_bp 非 byteswap 路径，不按 BP_SHOULD_BYTESWAP 分线
// 结果：大端写入小端读取时 DVA[2].word 与 blk_fill 解析错，salt/IV 全错→ECKSUM
```

## 9. 门禁

- **多图门禁**：`grep -c '```mermaid' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md` ≥3 且 `grep -c 'Source:' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md` ≥3 且每图附 `openzfs/zfs file:line`
- **溯源门禁**：`grep -q 'zio_crypt_table' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'ZIO_CRYPT_AES_128_GCM' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'ZIO_CRYPT_SM4_GCM' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'ZIO_STAGE_ENCRYPT' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md`
- **套件覆盖门禁**：`grep -q 'aes-128-ccm' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'aes-256-gcm' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'sm4-gcm' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'ZC_TYPE_GCM' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md`
- **transform 栈门禁**：`grep -q 'zio_push_transform' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_pop_transforms' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_encrypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_decrypt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'abd.*替换' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md`
- **IV/salt 门禁**：`grep -q 'zio_crypt_generate_iv' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_crypt_key_get_salt' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_crypt_generate_iv_salt_dedup' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'ZIO_DATA_IV_LEN' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md`
- **编码门禁**：`grep -q 'zio_crypt_encode_params_bp' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'zio_crypt_encode_mac_bp' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md && grep -q 'DVA\[2\]' records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md`
- **正文门禁**：`wc -l ontology/domain/zfs-crypto.md` ≥80 且 `grep -q '决策树' ontology/domain/zfs-crypto.md && grep -q '正例' ontology/domain/zfs-crypto.md && grep -q '反例' ontology/domain/zfs-crypto.md && grep -q '门禁' ontology/domain/zfs-crypto.md && grep -q 'Encrypt-Transform' ontology/domain/zfs-crypto.md`
- **属性门禁**：`attributes` 数量 ≥4 且每条 `testable_signal` 含 `grep -q` 动词+判定，且 `grep -q "zio_crypt" ontology/domain/zfs-crypto.md` 命中且 `grep -q "ZIO_STAGE_ENCRYPT" ontology/domain/zfs-crypto.md` 命中
- **本体校验**：`python3 scripts/ontology-validate.py --ontology-dir ontology` 0 issues 且 `python3 scripts/ontology_graph.py --format summary` `islands:0`
- **脚手架门禁**：`python3 scripts/ontology_test_scaffold.py --node ontology:domain/zfs-crypto --out /tmp/test_zfs_crypto_scaffold.py` 可产且 `pytest` 可收集
- **收敛门禁**：`python3 scripts/validate-convergence.py --task-dir pdca/tasks/0903-research-zfs-encrypt-transform` `valid:true`
- **T0500 回归门禁**：`grep -q 'Wrapping.*AES-256-CCM' ontology/domain/zfs-crypto.md` 仍命中（不破坏已有门禁）

Source: `openzfs/zfs/include/sys/fs/zfs.h:1954-1969`（`enum zio_encrypt`）+ `openzfs/zfs/include/sys/zio_crypt.h:46-72`（`zio_crypt_info_t`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:198-209`（`zio_crypt_table`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:361-384`（`zio_crypt_key_get_salt`）+ `openzfs/zfs/module/os/linux/zfs/zio_crypt.c:662-740`（`generate_iv/dedup`）+ `openzfs/zfs/module/zfs/zio.c:4953-5096`（`zio_encrypt` 七分支）+ `openzfs/zfs/module/zfs/zio.c:502-538`（`zio_push_transform`）+ `openzfs/zfs/module/zfs/zio.c:571-702`（`zio_decrypt`）+ `openzfs/zfs/include/sys/zio_impl.h:137`（`ZIO_STAGE_ENCRYPT`）+ `openzfs/zfs/include/sys/zio_impl.h:224-230`（`ZIO_WRITE_PIPELINE`）

## 10. 证据与追溯

- 调研报告：`records/T0500-0901-research-zfs-crypto/evidence/report.md`（AC-1~6 全覆盖，行号锚点）
- 调研报告（T0524 深化）：`records/T0524-0903-research-zfs-encrypt-transform/research-encrypt-transform.md`（AC-1 三图 + Source 全覆盖 `AES-128/256-GCM/CCM + SM4-GCM` 与 `ENCRYPT/DECRYPT` 压栈-弹栈）
- 收敛映射：`records/T0500-0901-research-zfs-crypto/evidence/convergence-map-v2.json`
- 收敛映射（T0524）：`records/T0524-0903-research-zfs-encrypt-transform/evidence/convergence.json`（回链 `meta.convergence`）
- 验证：`PYTHONPATH=scripts python3 -c "from pdca_core import convergence_issues"` 0 issue；`ontology-validate` 0 issue

## 11. 边界

- 基于 ZFS 工作树 + SM4 补丁的静态源码形态，未含运行时性能压测；SM4 zfs-tests 功能覆盖仍缺（建议新增）。
- 不替代国密合规审查，仅为工程实现层面的可复用领域模型。
- Transform 栈深度 `ZIO_TRANSFORM_STACK_DEPTH` 默认为 8，`ENCRYPT` 单次压栈不计压缩/分块，仅关注 `abd` 替换与 `salt/IV` 编码。
