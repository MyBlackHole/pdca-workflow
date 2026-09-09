# NBU数据加密实现研究报告（T2071，详细版）

> 对象：`/home/black/Public/aio/F/143/NBU`（NetBackup 10.3.0.1）
> 工具：`file / readelf / ldd / nm -D / strings / objdump -d / r2`
> 边界：仅 NBU 现状，不做 SM4 对比
> 证据：`evidence/01-21`，收敛见 `convergence-map-v5.json`

## 1. 总览：三链一底座

NBU 数据加密 = 底座密码库 + 三条落盘链 + 一套密钥管理：

- 底座：`libnbsslST.so（OpenSSL 1.1.0-fips-dev，NB_101_*）` + `libcmncryptoST / libcmncryptocoreST（EVPCrypter/GCMCrypter/mangle）` + `libkmsSH.so（kms*）`。
- 链 A 客户端备份加密：`bpkeyutil/bpkeyfile` 管钥 → `bpbkar EncryptBlock` 落密文像。
- 链 B 磁带介质加密：`bptm manage_drive_encryption` 按 `ENCR` 卷池向 KMS 取键，下发驱动器硬件加密。
- 链 C 磁盘/MSDP/云加密：`bpdm clientEncrypt/isEncrypted` 调 `mangle_aes_256_gcm_*`，`nbcryptocmd` 走 KMIP/GCM。
- 管钥面：`nbkmscmd` 管组/键/凭证（含 HMK/KPK 口令），`nbckmsutil` 管云，`nbcryptocmd` 管外部 KMIP。

```mermaid
flowchart TB
    BASE["底座<br/>libnbsslST 1.1.0-fips<br/>cmncryptocore GCM<br/>libkmsSH"]
    A["链A 客户端<br/>bpkeyutil/bpbkar"]
    B["链B 磁带<br/>bptm+KMS+驱动器"]
    C["链C 磁盘/MSDP/云<br/>bpdm+mangle/nbcryptocmd"]
    K["管钥面<br/>nbkmscmd/nbckmsutil"]
    BASE --> A & B & C
    K --> B & C
    A --> I1["备份像密文"]
    B --> I2["磁带密文"]
    C --> I3["磁盘密文"]
    Source0["来源：evidence/01/02/06/10/15，底座导出与加固"]
```

## 2. 底座深挖

### 2.1 版本与封装

`strings libnbsslST.so`（见 `01-ssl-version.txt`）：

```text
Big Number part of OpenSSL 1.1.0-fips-dev xx XXX xxxx
SHA1/SHA-256/SHA-512 part of OpenSSL 1.1.0-fips-dev xx XXX xxxx
OpenSSL FIPS 140-2 Public Key RSA KAT
FIPS 2.0.5 validated module 10 Apr 2013
NB_101_FIPS_mode / NB_101_FIPS_mode_set / NB_101_FIPS_module_version_text
```

`ldd` 显示 `bpkeyutil/bpbkar/bptm/bpdm/nbcryptocmd` 均依赖 `libcmncryptoST / libcmncryptocoreST / libnbsslST / libjanssonST`，与系统 OpenSSL 隔离。

### 2.2 完整对称算法导出（41 个，见 02/10）

- AES-128：`cbc/cfb/cfb128/ctr/ecb/gcm/ofb`（7）
- AES-192：`cbc/cfb/cfb128/ctr/ecb/gcm/ofb`（7）
- AES-256：`cbc/cfb/cfb128/ctr/ecb/gcm/ofb`（7）
- DES：`cbc/cfb/cfb64/ecb/ofb`（5）；3DES：`ede_cfb/ede_cfb64/ede_ofb/ede3_cbc/ede3_cfb/ede3_cfb64/ede3_ecb/ede3_ofb`（8）
- BF：`cbc/cfb/cfb64/ecb/ofb`（5）；Camellia：`128-cbc/256-cbc`（2）
- 合计 41，无 `EVP_sm*`（`07-sm4-count.txt=0`）。

### 2.3 摘要/随机/FIPS

`md5/sha1/sha256/sha512`、`RAND_seed`、`cmncrypto_getRandomBytes/mangleGetRandom`、`cmncrypto_getBinaryHash/CmnCrypto_hasher_*`、`FIPS_mode/mode_set/enable_fips_mode/testFipsCompliance`。

### 2.4 加固（见 15）

`bpkeyutil/bpbkar/bptm` 均为 `GNU_RELRO + BIND_NOW`，`bptm/bpdm` 为 PIE，`GNU_STACK` 不可执行；`gen_do_encryption` 含 `fs:0x28 canary + __stack_chk_fail`。动态库缺省不可解析属正常打包形态，不代表缺失。

## 3. 链 A：客户端备份加密（bpkeyutil/bpkeyfile/bpbkar）

```mermaid
flowchart LR
    P["口令输入<br/>GetNewPassPhrase"] --> D["32B派生<br/>Unable to generate the 32-byte key"]
    D --> S["选算法<br/>get_ciphertype_byname<br/>-ct"]
    S --> E["gen_do_encryption<br/>EncryptUpdate+Final"]
    E --> F["密钥文件<br/>read/write_key_file<br/>CLIENT_ENCRYPTION_KEY_PATH"]
    F --> B["bpbkar<br/>OpenEncryptFunctions→EncryptBlock"]
    B --> I["备份像<br/>.EnCrYpTiOn(.CiPhEr)+ENCRYPT_KIND"]
    SourceA["来源：evidence/03/04/08/11，bpkeyutil/bpbkar字符串与反汇编"]
```

### 3.1 bpkeyutil 算法表（见 03）

```text
AES-128-OFB、AES-192-CFB/OFB、AES-256-OFB/CTR/GCM、ALTAES-128/256-CFB
CAST5-CFB/OFB、DES-CFB/OFB、DES-EDE-CFB/OFB、DES-EDE3-CFB、DES_EDE3-OFB
RC2-CFB/OFB、RC4-40、RC5-CFB/OFB
```

导入 `NB_101_EVP_aes/des/bf/cast/rc` 全系；`r2 afl` 见 `gen_init_encryption/gen_do_encryption/gen_do_decryption/encrypt_passphrase/decrypt_passphrase/get_ciphertype_byname`。

`objdump gen_do_encryption`（见 08）：`malloc→EncryptUpdate→EncryptFinal→memcpy→free`，失败 `V_snprintf+logmsg+return -1`。

### 3.2 bpkeyfile/bpbkar 遗留 DES 路径（见 04/11）

`bpbkar` 字符串含 `DES_40/DES_56/default_libdes_path_40/56`，`bpkeyfile` 含 `libvdes40.so/libvdes56.so/GetDecryptedKeyFile/localDecryptKeyFile/ReadEncryptedKeyFile`。

`objdump OpenEncryptFunctions`：`dlopen(40)→dlsym 8个vdes_*→dlopen(56)→dlsym 2个→任一失败InternalErrorMessage+Close+return -1`。`EncryptBlock` 经 `vdes_cbc_encrypt_p` 间接调用，按块类型分流 `memcpy`。

口令提示区分标准与 NetBackup 口令：`Enter old/new key file pass phrase (standard...)` vs `Enter new NetBackup pass phrase`。

## 4. 链 B：磁带介质加密（bptm + KMS + 驱动器）

```mermaid
flowchart LR
    PO["ENCR卷池策略"] --> TM["bptm manage_drive_encryption<br/>get_encryption_key"]
    TM --> K["libkmsSH<br/>kmsGetKeyAndKad(ByKeyTag)/kmsGetKeysByKad"]
    K --> DK["kmsDecryptKey/kmsTransformKey"]
    DK --> DR["驱动器硬件加密<br/>DRIVE_ENCRYPTION_ACTIVE"]
    DR --> FR["无键冻结<br/>FREEZING ENCR pool"]
    SourceB["来源：evidence/05-bptm-kms.txt，bptm字符串"]
```

证据（见 05）：`FREEZING ... ENCR pool`、`DRIVE_ENCRYPTION_ACTIVE/BH_MAY_BE_ENCRYPTED`、`KMSCLIB::kmsGetKeyAndKad(ByKeyTag)/kmsGetKeysByKad/kmsDecryptKey/kmsTransformKey`、`begin writing encrypted backup id ... to (WORM) media`、`-fix_encrypt/FIX_ENCRYPT_KEYFILE`、`Encrypting data-in-transit/DTE IN-APP-TLS`。

`objdump -T bptm` 仅见 `CmnCrypto_hasher_*`，无 EVP 直调，证明加密下沉到库与硬件，bptm 只做调度与 KAD 标签管理。

## 5. 链 C：磁盘/MSDP/云加密（bpdm + mangle + nbcryptocmd）

```mermaid
flowchart LR
    D["待存数据"] --> M["mangle_aes_256_gcm_encrypt_with_rand_iv"]
    M --> R["mangleGetRandom 12B IV"]
    R --> E["EVP_aes_256_gcm<br/>Init→CTRL IV12→设key/IV→Update AAD/明文→Final→取Tag16"]
    E --> T["密文+Tag落MSDP/磁盘"]
    T --> F["bpdm clientEncrypt/isEncrypted/kmsKeyTag"]
    SourceC["来源：evidence/06/08/14，cmncryptocore/bpdm"]
```

`nm`（见 06）：`mangle_aes_256_gcm_encrypt_with_rand_iv/decrypt` + `EVPCrypter(7方法)` + `GCMCrypter(encrypt/decrypt/reset/getEncrypted/getDecrypted/add_authenticated_data_*)`。

`bpdm`（见 14）：`clientEncrypt/isEncrypted/kmsKeyTag/MSDPLB+/dedupeRatio/is_dedupe_to_cloud_storage/WORM lock/MSDP multi-domain`，去重与云共用同一调度。

`nbcryptocmd`（见 13）：自带 `GCMCrypter` + `NB_101_EVP_aes_256_gcm/FIPS_mode` + 全套 `NB_EKMS_KMIP::KMIP_* boost` 模板，为外部 KMIP 主力。

## 6. 管钥面深挖（nbkmscmd/nbckmsutil）

`nbkmscmd`（见 12）：`Key Group/Group Name/Info List`、`-createKey/-passphrasePath`、`HMK/KPK passphrase`（含 `Enter/Re-enter/Failed to read/did not match`）、`netbackup/security/passphrase-constraints`、`random passphrases`、`createKeyArg/createKeyRKSs`、`KMIP Attributes`。即组→键→凭证三级，HMK 护 KPK，KPK 护键口令，支持随机口令与文件口令。

## 7. 落盘形态与密钥生命周期

| 落盘 | 形态 | 取键 |
|---|---|---|
| 备份像 | `.EnCrYpTiOn(.CiPhEr)` 标记 + 密文 + `ENCRYPT_KIND` | 客户端密钥文件口令派生 32B 钥 |
| 磁带 | 驱动器硬件密文 + KAD 标签 | `ENCR` 卷池 → `kmsGetKeyAndKad(ByKeyTag)` → `kmsDecryptKey` |
| 磁盘/MSDP/云 | AES-256-GCM 密文 + 12B 随机 IV/次 + 16B Tag/次（多块则多组） | `clientEncrypt/kmsKeyTag` 或 KMIP |

口令丢、KMS 库丢即无法解密；`FIX_ENCRYPT_KEYFILE` 仅为修复镜像的离线手段。

## 8. 安全提示（secure-coding 视角）

- 新备份禁用 `DES_40/56、RC4-40、BF、CAST`，统一 `AES-256-GCM/CTR` 并开 FIPS。
- `dlopen libvdes` 路径须锁定权限，仅留读旧备份用途。
- KMS 的 HMK/KPK 口令文件与 `KMS_DATA` 分离备份，权限最小化，日志禁记口令。

## 4b. 加密逻辑逐函数深挖（本次补充）

### 4b.1 口令→32B 密钥派生（gen_32byte_digest + EVP_BytesToKey）

证据：`evidence/17/20`。字符串见 `Digest of PP is %02x...`、`Digest of key: %02X...`、`Unable to generate the 32-byte key from pass phrase`；反汇编见两次 `cmncrypto_getBinaryHash` 调用；底座导入 `NB_101_EVP_BytesToKey/get_digestbyname/DigestInit/Update/Final + BN_pseudo_rand`。

还原逻辑：口令经 `GetNewPassPhrase` 读入（两次须一致）→ `getBinaryHash` 得 H1 → 再哈希得 H2 → 截取 32B，另行 `gen_20byte_digest(key+iv)` 存校验，打开比对失败报 `key-iv digest does not match`。

### 4b.2 上下文初始化（gen_init_encryption）

证据：`evidence/16`。调用序 `memcpy(key)+memcpy(iv) → EVP_CIPHER_CTX_init → 间接取算法(*%rbp) → EVP_EncryptInit(空参) → set_key_length → EVP_EncryptInit装key/IV`，为变长密钥标准两步写法。

### 4b.3 块加密（gen_do_encryption）

证据：`evidence/08`。`malloc(2*len+1) → EncryptUpdate → EncryptFinal → 核对总长 → memcpy回写 → free`，失败 `logmsg+return -1`，栈 canary 完整。

### 4b.4 遗留 DES（EncryptBlock/2）

证据：`evidence/19`。`OpenEncryptFunctions → *vdes_cbc_encrypt_p → memcpy`，CBC 链式异或，弱密钥经 `is_weak_key/fixup_key_parity` 拒绝。

```mermaid
flowchart LR
    PP["口令"] --> H1["getBinaryHash→H1→H2→32B"]
    H1 --> CTX["CTX_init→选算法→设键长→装key/IV"]
    CTX --> UP["Update+Final→密文"]
    UP --> KF["密钥文件/备份块"]
    SourceK["来源：evidence/16/17/20"]
```

### 4b.5 GCM 加解密全序（mangle）

加密：`CTX_new→aes_256_gcm→Init空参→CTRL设IV12→随机IV→装key/IV→Update AAD/明文→Final→取Tag16`。解密（见18）：`CTX_new→DecryptInit空参→设IV→装key/IV→设Tag→Update→Final验Tag→free`，Tag 不对则失败防篡改。

```mermaid
flowchart TB
    A["CTX_new+aes_256_gcm"] --> B["设IV12+随机IV+装key"]
    B --> C["Update→Final→Tag16落盘"]
    C --> D["解密逆序Final验Tag"]
    SourceG["来源：evidence/06/08/18"]
```

### 4b.6 KMS 信封

`manage_drive_encryption→get_encryption_key→kmsGetKeyAndKad(ByKeyTag)/kmsGetKeysByKad→kmsDecryptKey→kmsTransformKey`，KAD 随带走，服务端只存密文+标签。

### 4b.7 Tag/IV 数量逻辑（一份数据多个 Tag）

结论先行：一份逻辑备份数据对应多个 Tag，不是单个 Tag。Tag 是单次 `(key + IV + 该块明文 + AAD)` 加密调用的认证输出，不是对数据的固定指纹。

证据：`evidence/21-tag-iv-asm.txt`（`mangle_aes_256_gcm_encrypt/decrypt` 反汇编）。

- 加密侧每次调用：`CTRL设IV长度 → malloc(0xc) 分配12字节IV → mangleGetRandom填充IV → 装key/IV → Update → Final → malloc(0x10) 分配16字节Tag → CTRL取出Tag`。即每次调用独立随机 IV、独立 Tag 缓冲。
- 解密侧每次调用：`设IV → 装key/IV → 设期望Tag → Update → Final验Tag → free`，Tag 不对则失败丢弃。
- 推论：备份数据按块/分片多次调用加密函数，每块各一个 `(IV, Tag)` 二元组落盘；同一明文重备一次，因 IV 随机，密文与 Tag 必然不同；校验与解密必须按块取对应 Tag，不存在全局单 Tag。

```mermaid
flowchart LR
    D["一份逻辑数据<br/>多块分片"] --> C1["调用1<br/>随机IV1→密文1+Tag1"]
    D --> C2["调用2<br/>随机IV2→密文2+Tag2"]
    D --> CN["调用N<br/>随机IVN→密文N+TagN"]
    C1 & C2 & CN --> S["落盘：密文块+IV+Tag三元组/块"]
    S --> V["解密按块取Tag验签"]
    SourceT["来源：evidence/21，malloc 0xc/0x10与CTRL对照"]
```

## 9. 结论与收敛映射

- AC-1：通过。ev-evp/ev-ciphers/ev-mangle/ev-geninit/ev-digest/ev-kdf 覆盖底座、工具表、GCM 封装与派生逻辑。
- AC-2：通过。ev-client/ev-tape/ev-bpkeyfile/ev-nbkms/ev-nbcrypt/ev-msdp/ev-mdec/ev-eb2/ev-tagiv 覆盖客户端、磁带、磁盘与 Tag/IV 逻辑，6 图每图 1 来源。
- AC-3：通过。ev-report/ev-map 覆盖报告与映射，复现命令如下。

## 10. 复现命令

```bash
strings NBU/lib/libnbsslST.so | grep -E "OpenSSL 1.1.0|FIPS"
nm -D NBU/lib/libnbsslST.so | grep -E "EVP_(aes|des|bf|camellia)"
strings NBU/bin/bpkeyutil | grep -E "^(AES|DES|CAST|RC|ALTAES)"
strings NBU/bin/bpkeyfile | grep -E "pass phrase|vdes|EncryptKeyFile"
strings NBU/bin/bpbkar | grep -E "vdes_|EnCrYpTiOn|ENCRYPT_KIND"
strings NBU/bin/bptm | grep -E "kmsGetKey|manage_drive_encryption|ENCR pool"
strings NBU/bin/bpdm | grep -E "MSDP|clientEncrypt|kmsKeyTag"
strings NBU/bin/nbkmscmd | grep -E "Key Group|HMK|KPK|KMIP"
nm -D NBU/lib/libcmncryptocoreST.so | grep -E "mangle_aes|GCMCrypter"
nm -D NBU/bin/nbcryptocmd | grep -E "GCM|KMIP|FIPS"
objdump -d NBU/bin/bpkeyutil --disassemble=gen_do_encryption | grep EVP_Encrypt
objdump -d NBU/lib/libcmncryptocoreST.so --disassemble=mangle_aes_256_gcm_encrypt_with_rand_iv | grep -E "aes_256_gcm|mangleGetRandom"
objdump -d NBU/bin/bpkeyutil --disassemble=gen_init_encryption | grep -E "CIPHER_CTX_init|EncryptInit|set_key_length"
objdump -d NBU/bin/bpkeyutil --disassemble=gen_32byte_digest | grep getBinaryHash
objdump -d NBU/lib/libcmncryptocoreST.so --disassemble=mangle_aes_256_gcm_decrypt | grep -E "DecryptInit|DecryptUpdate|DecryptFinal"
readelf -l NBU/bin/bptm | grep -E "GNU_STACK|GNU_RELRO"
objdump -d NBU/lib/libcmncryptocoreST.so --disassemble=mangle_aes_256_gcm_encrypt_with_rand_iv | grep -B2 -A1 "malloc@plt\|CIPHER_CTX_ctrl@plt\|mangleGetRandom" | grep -E "mov.*0x(c|10)|call"
objdump -d NBU/bin/bpkeyutil --disassemble=gen_init_encryption | grep -E "EVP_CIPHER_CTX_init|EncryptInit|set_key_length"
objdump -d NBU/bin/bpkeyutil --disassemble=gen_32byte_digest | grep cmncrypto_getBinaryHash
objdump -d NBU/lib/libcmncryptocoreST.so --disassemble=mangle_aes_256_gcm_decrypt | grep -E "DecryptInit|DecryptUpdate|DecryptFinal"
```
