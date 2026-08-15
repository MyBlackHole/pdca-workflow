# Triage Brief — T0249

- **分类**: enhancement / research（源码级实证既有国密支撑面结论）
- **需求**: 解压 `/home/black/Downloads/kernel-OLK-6.6.zip`（openEuler OLK 6.6 内核源码，92265 条目，292MB），研究其中 NFS 是否支持国密（SM2/SM3/SM4）
- **查重**: 无既有 kernel-OLK-6.6 解压/研究任务；knowledge/backup-crypto/gm-support-surfaces.md 第 3 节有相关断言——"内核 crypto 层注册国密、NFS 的 RPCSEC_GSS/krb5 enctype 白名单仅含国际算法、NFS 不调用国密"。本任务为**源码级实证/验证**该结论，非重复
- **事实核查**:
  - zip 可读：92265 条目，含 `kernel-OLK-6.6/fs/nfs/`（199 文件）、`net/sunrpc/auth_gss/`（gss_krb5 相关 19 处）、`crypto/` sm4/sm3（32 处）、arm64 sm3/sm4 CE 加速（存在）
  - 待解压后核查关键路径：`net/sunrpc/auth_gss/gss_krb5_mech.c`（enctype 白名单）、`gss_krb5_crypto.c`、NFS 是否引用 sm4/sm3
- **关键未知（需 P1/P2 决策）**: 解压目标目录、研究深度（仅 NFS 客户端/服务端 + GSS 协商路径 vs 全内核国密支持点枚举）

---

## 核查命令记录

```
python3 -c "zipfile.ZipFile(...); namelist()"  # 92265 条目
fs/nfs 199 文件；net/sunrpc/auth_gss 19；crypto sm4/sm3 32；arm64 sm3/sm4 CE 存在
```
