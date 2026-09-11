---
schema: pdca.asset/v2
id: ontology:pattern/gm-symmetric-modes
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/gm-symmetric-modes/3.1.0
summary: 模式选型研究边界：先固定协议与支持证据
relations:
  guides:
  - ontology:domain/encryption-modes
  - ontology:domain/gm-algorithm-suite
  relates_to:
  - ontology:domain/backup-crypto-gm-support-surfaces
  instance_of:
  - ontology:pattern
attributes:
- name: source_binding
  desc: 导航不构成算法或产品实现证据
  constraint: 以对应模式的固定来源、任务适用范围和真实测试为准
  testable_signal: 检查claim-review来源与固定版本；向量见tests/crypto-regression.md，链接存在只作结构检查
  evidence_level: source
revision: 3.1.0
authority: reference
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# 对称模式选型：任务需要决定的内容

本节点仅组织选型问题，不发布未经核验的硬件能力或性能排序。旧版决策图中的模式归属和绝对化判定撤回，原文保留在v3归档/补丁。

选型任务首先固定数据访问和认证单位、兼容协议、持久化布局、nonce生命周期、密钥管理、允许副作用及威胁边界。再从[模式索引](../domain/core/encryption-modes.md)选择候选，核验具体标准与构建支持，使用正反向互通测试决定是否符合目标。

GCM/CCM不是全部认证加密方案的穷举。XTS固定key/tweak/plaintext会重复产生相同密文，不能据此提供版本变化认证。CFB与CBC-CTS不是同一模式。具体纠错依据与向量只保留在对应模式节点，避免这里再建一套oracle。

GM/T、SDF卡能力、CPU内核加速及私有SM4-ZFS支持需提供准确版本、接口注册、构建和实测证据；此前历史任务号不能当作当前部署支持证明。性能结论必须用目标平台和数据尺寸对比，不凭“并行”推断最佳。相关事实未核验时不写进必需验收条件。

采用前填写claim-review；本页仍是unverified研究导航，不自动认证全部链接或特定产品。
