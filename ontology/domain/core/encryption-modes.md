---
schema: pdca.asset/v2
id: ontology:domain/encryption-modes
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/encryption-modes/3.1.0
summary: 工作模式索引：不复制算法公式作为第二权威
relations:
  relates_to:
  - ontology:domain/backup-crypto-gm-support-surfaces
  - ontology:domain/backup-crypto
  instance_of:
  - ontology:concept/knowledge-artifact
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

# 分组密码模式资料索引

本页是导航，不再复制未经验证的“最佳/唯二/通用12B”选型表或第二套公式。具体模式定义与限制只按固定版本节点采用：

| 节点 | 采用时必须核对 |
|---|---|
| [GCM](../../concept/cipher-mode-gcm.md) | H与标签掩码J0分离、格式化、nonce管理、具体tag长度与向量 |
| [CCM](../../concept/cipher-mode-ccm.md) | M/L、B0、AAD编码、必要补零、S0掩码 |
| [XTS](../../concept/cipher-mode-xts.md) | 数据单元tweak、GF推进、尾块、确定性和没有认证 |
| [CFB](../../concept/cipher-mode-cfb.md) | 不与CBC-CTS混同，实际协议与库能力需版本匹配 |

原页重复的错误GCM掩码和固定XTS输入不同输出结论已撤回。列表不是全部AEAD的穷举，也不推导所有存储都应选某一模式。随机读取能否独立认证取决于实际认证单元、布局与协议，不能从“CTR可寻址”直接推出。

测试采用[公开向量与错误变体](../../../tests/crypto-regression.md)；各引用节点仍须claim-review。其他模式节点未因本索引修正而自动获得事实认证。
