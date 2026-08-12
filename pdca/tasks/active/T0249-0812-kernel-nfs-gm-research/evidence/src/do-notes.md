# kernel-OLK-6.6 NFS 国密支持研究 — Do 证据说明

## 结论摘要

**kernel-OLK-6.6 的 NFS 数据面协议层不支持原生国密**（SM2/SM3/SM4）。内核 crypto 层注册了国密算法且若干子系统（TLS/IPsec/fscrypt）已支持国密，但 NFS 的 GSS/krb5 数据面协商白名单仅含国际算法，NFS 代码路径零国密引用。NFS 国密只能经链路层叠加（NFS-over-TLS/IPsec），而内核 net/tls 的 SM4-GCM/CCM 支持为 NFS-over-TLS 叠加国密提供了前提。

## 证据链

### AC-2: RPCSEC_GSS/krb5 enctype 白名单算法集
文件 `net/sunrpc/auth_gss/gss_krb5_mech.c` 的 `supported_gss_krb5_enctypes[]`（L33 起）：

| enctype | encrypt_name | cksum_name | RFC |
|---------|--------------|------------|-----|
| aes128-cts | cts(cbc(aes)) | hmac(sha1) | 3962 |
| aes256-cts | cts(cbc(aes)) | hmac(sha1) | 3962 |
| camellia128-cts-cmac | cts(cbc(camellia)) | cmac(camellia) | 6803 |
| camellia256-cts-cmac | cts(cbc(camellia)) | cmac(camellia) | 6803 |
| aes128-cts-hmac-sha256-128 | cts(cbc(aes)) | hmac(sha256) | 8009 |
| aes256-cts-hmac-sha384-192 | cts(cbc(aes)) | hmac(sha384) | 8009 |

- 编译开关：`CONFIG_RPCSEC_GSS_KRB5_ENCTYPES_{AES_SHA1,CAMELLIA,AES_SHA2}`（net/sunrpc/Kconfig L37/50/62）
- **无任何 sm4/sm3/sm2 enctype**；优先级列表 `gss_krb5_enctypes[]`（L214）同样仅上述 6 项国际算法
- NFS sec= 选项仅 krb5/krb5i/krb5p + 未实现的 lkey/spkm（fs/nfs/fs_context.c L454-478；SPKM 在 auth_gss 无实现）

### AC-3: fs/nfs + fs/nfsd 国密引用
`rg -l 'sm4|sm3|sm2' fs/nfs fs/nfsd net/sunrpc` → **0 命中**。NFS 客户/服务端代码路径不引用任何国密算法。

### AC-4: crypto 层国密注册佐证
- `crypto/sm4_generic.c` L58 `.cra_name = "sm4"`（synchronous cipher）
- `crypto/sm3.c`、`crypto/sm2.c`（`cra_name="sm2"`，L474）存在
- arch 加速：`arch/arm64/crypto/sm4-ce-glue.c`、`arch/arm64/crypto/sm3-ce-glue.c` 存在

### 佐证：内核其他子系统已接入国密（叠加路径可行性）
| 子系统 | 支持 | 说明 |
|--------|------|------|
| net/tls | TLS_CIPHER_SM4_GCM / SM4_CCM（`gcm(sm4)`/`ccm(sm4)`，tls_main.c L106-107） | 内核 TLS 支持 SM4（RFC 8998 国密 TLS） |
| net/xfrm (IPsec) | `hmac(sm3)`（xfrm_algo.c L345）、`cbc(sm4)`（L576） | IPsec 算法注册含国密 |
| fs/crypto (fscrypt) | SM4-XTS、SM4-CTS-CBC（keysetup.c L47-57） | 文件静态加密支持国密 |
| NFS xprtsec | `xprtsec=tls/mtls`（fs/nfs/fs_context.c L296-299；net/sunrpc/xprtsock.c 实现） | NFS-over-TLS 挂载选项存在 |

## 结论推论

1. NFS 数据面（RPCSEC_GSS/krb5 协商）**无法原生国密**——enctype 白名单硬编码国际算法
2. NFS 国密需链路层叠加：OLK-6.6 支持 `xprtsec=tls` 且内核 net/tls 已注册 SM4-GCM/CCM，从源码上看 **NFS-over-TLS(国密 SM4) 具备实现前提**（实际协商依赖用户态 TLS 卸载/证书密钥环）
3. 佐证既有 `backup-crypto/gm-support-surfaces.md` 第 3 节结论：注册能力 ≠ 协议调用路径