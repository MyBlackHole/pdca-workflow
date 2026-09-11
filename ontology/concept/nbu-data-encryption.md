---
schema: pdca.asset/v2
id: ontology:concept/nbu-data-encryption
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-07
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/nbu-data-encryption/3.1.0
summary: NBU加密研究资料实例；历史推断待原始二进制与记录核验，不继承任务类
relations:
  relates_to:
  - ontology:concept/cipher-mode-gcm
  - ontology:concept/cipher-mode-cfb
  - ontology:concept/cipher-mode-cbc
  - ontology:concept/pdca-task
  instance_of:
  - ontology:concept/knowledge-artifact
attributes:
- name: evidence_required
  desc: 历史研究对象需固定来源
  constraint: 客户端/磁带/磁盘/KMS路径为待核对研究维度，不是已证实现合同
  testable_signal: 取得版本、二进制摘要、调用证据、配置与实际样本后逐主张验证
  evidence_level: unclassified
revision: 3.1.0
authority: reference
semantic_kind: individual
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: quarantined
  adoption: blocked
  checked_claims:
  - KNOWLEDGE_ARTIFACT_NOT_PDCA_SUBCLASS
  runtime_validation: not_run
---

# NBU加密研究资料：知识产物实例

本文件是一份KnowledgeArtifact，不是pdca-task的子类。与任务只有主题应用关联，不继承任务身份/生命周期。

原资料引用NetBackup 10.3.0.1、T2071及反汇编输出，但原始输入未随包提供。客户端、磁带、磁盘与管钥面可以作为后续核验目录，不把旧函数名、套件支持或密钥派生推断写成强制实现规则。本节点暂不允许采用为验收依据。

“随机IV所以重备必变”也不能作为确定性测试oracle：随机选择仍有碰撞可能；调用粒度与保存方式需真实证据，不能由一次malloc大小推出全部备份格式。GCM公式采用已纠正的独立节点，不从历史推断反向生成。

补证要求：产品/组件/配置/二进制版本及摘要、可定位原报告和上下文、授权测试输入、实际加解密与失败样本。采用时逐条区分事实、推断、未知，测试正常路径和错误密钥/篡改/不支持配置；原记录缺失不等于产品不存在这些功能。
