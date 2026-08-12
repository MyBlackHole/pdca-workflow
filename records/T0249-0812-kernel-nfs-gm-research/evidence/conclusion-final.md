---
schema: pdca.asset/v1
id: T0249-0812-kernel-nfs-gm-research
phase: check
source_ids: [do-notes, kernel-src-evidence, conclusion-draft]
---

## 上下文

用户请求按 PDCA 流程解压 `/home/black/Downloads/kernel-OLK-6.6.zip`（openEuler OLK 6.6 内核源码，92265 条目 / 1.6G 解压），研究 NFS 是否支持国密。方向确认为聚焦 NFS 数据面（gss 白名单 / fs-nfs / fs-nfsd / crypto 佐证），实证既有 `backup-crypto/gm-support-surfaces.md` 第 3 节断言。用户批准 PRD 全案，AC-1~AC-5。

## 假设与结果

| 假设 | 结果 |
|------|------|
| OLK-6.6 crypto 层注册国密 | ✅ `crypto/sm4_generic.c`(cra_name="sm4")、`sm3.c`、`sm2.c` + arm64 sm4/sm3 CE 加速存在 |
| NFS GSS/krb5 enctype 白名单仅国际算法 | ✅ `gss_krb5_mech.c` 6 个 enctype 全为 aes/camellia + hmac-sha1/sha256/sha384 |
| NFS 数据面无国密引用 | ✅ `rg 'sm4|sm3|sm2' fs/nfs fs/nfsd net/sunrpc` = 0 |
| NFS 有国密叠加前提 | ✅ `xprtsec=tls/mtls` + net/tls 注册 SM4-GCM/CCM |

## 分析

### AC 达成情况
- **AC-1** ✅: 解压至 `/home/black/Downloads/kernel-OLK-6.6-src/kernel-OLK-6.6/`
- **AC-2** ✅: `gss_krb5_mech.c:33` `supported_gss_krb5_enctypes[]` 白名单 6 项：aes128/256-cts(+hmac-sha1)、camellia128/256-cts-cmac、aes128-cts-sha256/aes256-cts-sha384；编译开关 `CONFIG_RPCSEC_GSS_KRB5_ENCTYPES_{AES_SHA1,CAMELLIA,AES_SHA2}`
- **AC-3** ✅: fs/nfs、fs/nfsd、net/sunrpc 对 sm4/sm3/sm2 引用 0 命中；NFS sec= 仅 krb5/krb5i/krb5p（lkey/spkm 未实现）
- **AC-4** ✅: crypto 注册 sm4/sm3/sm2 + arm64 CE 加速（注册能力佐证）
- **AC-5** ✅: 结论产出 + 知识资产更新（Act 阶段落地）

### 核心结论
**OLK-6.6 的 NFS 数据面协议层不支持原生国密**：
1. GSS/krb5 enctype 白名单硬编码国际算法（RFC 3962/6803/8009），无 sm4/sm3/sm2
2. NFS 客户/服务端代码路径零国密引用
3. 内核 crypto 层已注册国密；net/tls 注册 SM4-GCM/CCM、xfrm 注册 hmac(sm3)/cbc(sm4)、fscrypt 支持 SM4-XTS/CTS
4. NFS 支持 `xprtsec=tls/mtls` → **NFS-over-TLS(SM4-GCM/CCM) 叠加路径具备实现前提**

**xprtsec 机制边界（源码级，T0249 澄清）**：
- `xprtsec=tls/mtls`（fs/nfs/fs_context.c:290-299）指示 NFS 客户端在 TCP 之上建立 TLS 会话，认证用 `RPC_AUTH_TLS`（net/sunrpc/xprtsock.c:2664）
- 内核侧只负责发起握手：`tls_client_hello_anon`（tls）/`tls_client_hello_x509`（mtls，证书+私钥取自 kernel keyring `cert_serial`/`privkey_serial`，xprtsock.c:2609-2620）
- **完整 TLS handshake（算法协商、证书校验）由用户态 handshake daemon（如 tlshd/ktls-utils）完成**；内核 SM4-GCM/CCM（tls_main.c:106-107，RFC 8998 国密 TLS）`offloadable=false`，走软件路径
- 因此要协商出 SM4：用户态 TLS 栈须支持 RFC 8998 国密套件，且 NFS 服务器端同样可配 SM4——这是"前提"而非"已支持"的边界所在

佐证既有知识"注册能力 ≠ 协议调用路径"。该结论与 `gm-support-surfaces.md` 第 3 节一致，并新增 OLK-6.6 源码证据 + NFS-over-TLS 叠加可行性的正向佐证。

## 失败原因（仅 rejected/partial）

不适用 — 结论 confirmed。

## 适用边界

- 基于静态源码证据，未运行内核/未实测 `mount -o sec=` 协商
- NFS-over-TLS 国密叠加为**前提性**结论：内核 xprtsec+tls 已具备，但完整协商依赖 openssl/kernel TLS 用户态卸载与国密证书链，需实测确认
- OLK-6.6 特定结论；其他内核版本 enctype 白名单可能演进

## 下一轮建议

- 如需落地 NFS 国密备份链路：实测 NFSv4.2 `xprtsec=tls,sec=sys`（或 krb5）叠加 SM4 TLS，验证用户态 tlshd/openssl 国密套件协商；或走 IPsec（xfrm 已注册 cbc(sm4)/hmac(sm3)）
- 如需补丁级验证：检查 openEuler 用户态（krb5/gssproxy/openssl/tlshd）是否已配置 SM4 支持对齐内核 net/tls