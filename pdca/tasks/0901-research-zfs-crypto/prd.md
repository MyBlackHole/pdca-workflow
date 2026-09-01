# 调研 OpenZFS 加解密实现

## Goal

对 OpenZFS（本仓库，含 SM4-GCM 扩展补丁）中加解密体系做系统性调研，形成可追溯到源码的调研报告，覆盖算法套件、密钥管理、数据路径、磁盘格式、校验完整性及用户接口，为后续 SM4-GCM 国密化及安全审计提供依据。

## Requirements

- 梳理 ZIO 加密套件枚举、参数表 `zio_crypt_table` 及对应 ICP 算法实现（AES-CCM/GCM、SM4-GCM）与模式层 CCM/GCM。
- 梳理密钥体系：wrapping key（用户口令派生 PBKDF2/HKDF）、master key、DSL Crypto Key ZAP 存储、spa_keystore 三棵 AVL 树（wkey / master key / mapping）、load/unload/change 流程。
- 梳理数据路径：zio 层加解密入口、IV/MAC 生成与校验、abd 加解密、ARC/DMU/bpobj 集成、send/recv 原始流处理。
- 梳理磁盘格式与属性：blkptr 加密位、DVA、L2ARC、dataset 属性 `encryption`/`keyformat`/`keylocation`/`pbkdf2iters` 等及 zfs_prop 约束。
- 梳理完整性与校验：MAC、checksum 与加密交互、加解密失败处理。
- 梳理平台适配：Linux QAT 加速路径、FreeBSD crypto 适配、SM4-GCM 新增改动点及 KCF provider 注册。

## 关联本体节点

```
ontology:domain/backup-crypto
ontology:domain/backup-crypto-gm-support-surfaces
ontology:domain/backup-crypto-medium-model
ontology:concept/pdca-task
```

## 拆分映射

- 算法套件 -> ontology:domain/backup-crypto
- 密钥管理 -> ontology:domain/backup-crypto-medium-model
- 国密适配 -> ontology:domain/backup-crypto-gm-support-surfaces

## 验收标准

- [ ] AC-1 加密算法套件与参数已梳理：明确 ZIO_CRYPT 枚举、zio_crypt_table 参数（keylen/ivlen/maclen/blocksize）、ICP 提供者注册、CCM/GCM 模式差异及 SM4 扩展
- [ ] AC-2 密钥管理与生命周期已梳理：明确 wrapping key vs master key、PBKDF2/HKDF 派生、DSL Crypto Key ZAP、spa_keystore 三树设计、load/unload/change/inherit 流程与引用计数
- [ ] AC-3 数据加密/解密路径与调用链已梳理：明确 zio_encrypt_decrypt 等入口、IV 随机生成、abd 加密、arc/dmu 读写路径、send/recv raw 处理及错误语义
- [ ] AC-4 On-disk格式与属性接口已梳理：明确 blkptr/dnode/objset 加密标记、dataset 属性（encryption/keyformat/keylocation/pbkdf2*）、zfs(8) 用户命令与 libzfs 封装
- [ ] AC-5 校验与完整性机制已梳理：明确 MAC 校验、checksum 与加密顺序、损坏/篡改检测与修复策略
- [ ] AC-6 SM4-GCM扩展及QAT/FreeBSD适配已梳理：明确 SM4 128-bit 实现、GCM_USE_GENERIC 改动、qat_crypt 拒绝回退、FreeBSD 机制表与补丁影响面
- [ ] AC-7 报告已登记且收敛映射可验证：调研报告、convergence-map、evidence manifest 完整且校验通过

## 非目标

- 不做性能压测对比（仅引用代码中的性能分支说明）
- 不改动加密逻辑本身，纯结论性调研
