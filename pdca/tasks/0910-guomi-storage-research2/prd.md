# 存储国密落改调研重做（T2125·纯调研）

## 背景

T2107本体缺三块（NFS独立表达、密钥全量、门禁灰度）且三原因已修（T2115归档），本次用新流程重做：AC逐章映射、Grill覆盖必问、覆盖脚本验收。

Grill（round1-2，均captured:true）：范围=三类全覆盖行号级；沉淀=R4+NFS独立表达+密钥门禁补项；章节清单=S3三态/读自适应/NFS清单/密钥管理/升级门禁/灰度。

## 目标

产出全覆盖`research-report.md` + 本体一次写全（R4与补项），覆盖脚本零警告，不改代码。

## 范围

输入：方案文档 + 本仓源码。输出：报告 + 本体修订。不做：不改代码、不跑实测。

## 验收标准

- [ ] AC-1: S3三态写覆盖方案§3.2（`--gmssl`口径、`sm4-nonce`、`file-size`），行号可复核
- [ ] AC-2: 读端自适应与升级门禁覆盖方案§3.2/§3.4（对象分支、fail-closed、读端先行、旧挂载点清理）
- [ ] AC-3: NFS清单覆盖方案§3.3（`--enc-algo`语义、算法/nonce/长度/校验和四字段、半写收敛）
- [ ] AC-4: 密钥管理覆盖方案§四（收发同钥、分离存放、轮换另立项、丢钥丢数据）
- [ ] AC-5: ZFS承接与灰度覆盖方案§3.1/§3.5/Y1-Y7（建卷参数、send/recv继承、内测灰度、Y对齐矩阵）
- [ ] AC-6: 本体沉淀：storage-R4+NFS独立表达+密钥门禁补项，覆盖脚本零警告
- [ ] AC-7: 全程零代码改动（目标仓`git status`干净）

## 关联本体节点

```
ontology:pattern/sm4-storage-encryption
ontology:pattern/sm4-s3-encryption
ontology:pattern/sm4-zfs-encryption
ontology:concept/pdca-task
ontology:concept/pdca-evidence
ontology:concept/pdca-verdict
```

## 拆分映射

- S3三态与读端（§3.2/§3.4） -> ontology:pattern/sm4-s3-encryption
- NFS清单（§3.3） -> ontology:pattern/sm4-storage-encryption
- 密钥管理（§四）与门禁灰度 -> ontology:pattern/sm4-storage-encryption
- ZFS承接（§3.1/§3.5） -> ontology:pattern/sm4-zfs-encryption
