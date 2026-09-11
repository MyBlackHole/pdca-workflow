---
schema: pdca.asset/v2
id: ontology:pattern/sm4-zfs-encryption
type: pattern
layer: Knowledge
status: active
summary: 私有SM4-ZFS扩展候选：缺固定实现，禁止当上游通用操作
relations:
  relates_to:
  - ontology:entity/zfs-system
  - ontology:pattern/sm4-storage-encryption
  instance_of:
  - ontology:pattern
attributes:
- name: private_build
  desc: 私有扩展必须绑定版本
  constraint: 套件注册、密钥加载与send/receive规则均须匹配实际分支证据
  testable_signal: 提交commit/补丁、构建、能力探测和受控读回；设计文字/grep不证明支持
  evidence_level: unclassified
revision: 3.1.0
authority: reference
dcterms_modified: '2026-09-12'
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
  content_review: 2026-09-12; pinned sources only; not latest-release certification
validation:
  claim_status: quarantined
  adoption: blocked
  checked_claims:
  - UPSTREAM_ZFS_2_3_0_PROPERTY_SCOPE
  source_refs:
  - https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/man/man7/zfsprops.7
  runtime_validation: not_run
---

# SM4-ZFS：私有扩展候选，不是通用命令手册

**adoption=blocked。** 本节点保留方案线索，不断言私有实现不存在。F/139、T2107及内核源码未随本包提供，旧`encryption=sm4-gcm`、load-key与send/receive属性继承说明不再作为可执行步骤。

[上游zfs-2.3.0属性文档](https://raw.githubusercontent.com/openzfs/zfs/zfs-2.3.0/man/man7/zfsprops.7)的encryption套件表列出AES选项，不能由此给其他分支编造SM4支持，也不能据此否定用户私有扩展。

## 补证及单元测试

必须提供源码commit/补丁、构建身份与套件注册、授权隔离环境。正例应独立覆盖创建/加载密钥/写入读回；send/receive明确raw与非raw、目标属性、密钥可用性及失败条件。反例包括未知套件、错误密钥、错误构建、属性不兼容和只有设计文档却声称功能已运行。

每例固定输入、预期错误/成功及禁止明文降级，记录真正运行结果和版本。材料不全时保留unverified/blocked，不能用目标项目的“已安装”自述代替证据。解除隔离需新版本与内容审查。
