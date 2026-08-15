# kernel-OLK-6.6 NFS 国密支持研究 — 结论（草案）

- **AC-1** ✅: `/home/black/Downloads/kernel-OLK-6.6-src/kernel-OLK-6.6/` 解压完成（1.6G，92265 条目）
- **AC-2** ✅: `net/sunrpc/auth_gss/gss_krb5_mech.c` enctype 白名单仅含国际算法（aes/camellia + hmac-sha1/sha256/sha384），**无 sm4/sm3/sm2**
- **AC-3** ✅: `rg 'sm4|sm3|sm2' fs/nfs fs/nfsd net/sunrpc` → **0 命中**
- **AC-4** ✅: crypto 层注册 `sm4`/`sm3`/`sm2`（含 arm64 CE 加速），佐证注册能力存在
- **AC-5** ✅: 结论产出（见 record conclusion）并更新 gm-support-surfaces.md 添加 OLK-6.6 源码证据

## 核心结论

**OLK-6.6 的 NFS 数据面协议层不支持原生国密**：GSS/krb5 enctype 白名单硬编码国际算法，NFS 代码路径零国密引用。但内核 crypto 层注册了国密；net/tls 已注册 SM4-GCM/CCM、xfrm 注册 hmac(sm3)/cbc(sm4)、fscrypt 支持 SM4-XTS，且 NFS 支持 `xprtsec=tls/mtls`——**NFS-over-TLS(SM4) 叠加路径具备实现前提**。佐证既有 gm-support-surfaces 结论"注册能力 ≠ 协议调用路径"。