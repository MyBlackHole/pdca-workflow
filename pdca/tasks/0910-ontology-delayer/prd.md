# 本体混层重构（T2143·bugfix）

## 背景

T2107/T2125沉淀把一次性落改清单写进长期模式节点（R3/R4含行号改法）、NFS两处重复、signal指records自证。
复现命令见`research-report.md`三节。T2144/2145/2146为叶分解，子agent并行，母票集成。

Grill（round1-2，均captured:true）：三项全做；子agent并行。

## 目标

模式节点只留规则模型，任务痕迹只留来源行；细节归叶、storage留指针；signal指稳定源。

## 范围

输入：`sm4-storage-encryption.md`（R3/R4区）、`sm4-nfs-encryption.md`、`sm4-s3-encryption.md`、`sm4-zfs-encryption.md`。
输出：四处修订 + 验证证据。不做：不动flow标准流程、不增新节点（去重用现有）、不碰他人在改文件。

## 验收标准

- [ ] AC-1: storage去任务化：R3/R4正文无行号无“改为/新增”动作词，只留规则模型+来源record行
- [ ] AC-2: NFS单源：四字段细节只留nfs节点，storage只留一句话指针；signal改指代码仓与方案文档
- [ ] AC-3: s3/zfs规范：修订节瘦身为来源行+指针，无复述清单
- [ ] AC-4: 回归：`ontology-validate`全绿，T2125沉淀校验仍通过，覆盖脚本严格词表零警告
- [ ] AC-5: 无残留：`grep -n "main.cpp\|fuse-file\|obs-service\|rpc-common" ontology/pattern/sm4-*.md`在正文区零命中（来源行与signal除外，逐条豁免说明）

## 关联本体节点

```
ontology:pattern/sm4-storage-encryption
ontology:pattern/sm4-nfs-encryption
ontology:pattern/sm4-s3-encryption
ontology:pattern/sm4-zfs-encryption
ontology:concept/pdca-task
ontology:concept/pdca-evidence
```

## 拆分映射

- storage去任务化（T2144） -> ontology:pattern/sm4-storage-encryption
- NFS去重signal（T2145） -> ontology:pattern/sm4-nfs-encryption
- s3zfs规范（T2146） -> ontology:pattern/sm4-s3-encryption
