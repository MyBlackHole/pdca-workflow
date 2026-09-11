---
schema: pdca.asset/v2
id: ontology:concept/cipher-mode-gcm
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/cipher-mode-gcm/3.1.0
summary: GCM：区分H、J0与标签，固定标准与向量，不用关键词证明算法
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
  - ontology:concept/cipher-mode
attributes:
- name: tag_construction
  desc: H不等于标签掩码
  constraint: H=E_K(0^128)；T=MSB_t(E_K(J0) xor S)
  testable_signal: 按tests/crypto-regression.md固定向量逐字节核对；使用H代替E_K(J0)的变体必须失败
  evidence_level: behavior
- name: nonce_and_lengths
  desc: 参数适用范围
  constraint: 同key的IV须按固定协议满足唯一性；标签是离散支持值，不是32至128的连续区间
  testable_signal: 核验固定版本标准与当前任务选定参数，缺少nonce管理证据不能认定安全
  evidence_level: source
revision: 3.1.0
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
  content_review: 2026-09-12; pinned sources only; not latest-release certification
validation:
  claim_status: source_checked_scoped
  adoption: claim_review_required
  checked_claims:
  - GCM_TAG
  - GCM_FORMAT
  - GCM_TAG_LENGTH
  source_refs:
  - https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
  - https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/test/recipes/30-test_evp_data/evpciph_aes_common.txt
  runtime_validation: not_run
---

# GCM：认证加密的定义边界

本条按NIST SP 800-38D（2007）§5.2/7/8限定算法；不是对2026年最新修订、SM4产品支持或具体加速代码的认证。[标准](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)

## 构造（长度均为bit）

`H=E_K(0^128)`。96位IV时`J0=IV||0^31||1`；其他允许长度按标准GHASH格式派生，不能直接拼接/截断。`C=GCTR_K(inc32(J0),P)`。

令`v=(-len(A)) mod 128`、`u=(-len(C)) mod 128`：
`S=GHASH_H(A||0^v||C||0^u||[len(A)]_64||[len(C)]_64)`，64位长度以大端编码。
`T=MSB_t(E_K(J0) xor S)`。`H`负责GHASH乘法，`E_K(J0)`负责标签掩码，二者不可互换。

该固定标准的t为128/120/112/104/96 bit，32/64 bit另有短标签使用限制；实现可以支持更小子集，但不能虚构任意长度。当前教学回归固定128 bit，不构成短标签部署建议。同key下IV不可重用；P受标准长度上限约束。验证失败不得把候选明文交给应用。

## 单元测试与错误定义反例

[固定向量与变体](../../tests/crypto-regression.md)覆盖空消息、单块、带AAD非整块、非96位IV，以及标签/AAD/密文/IV篡改。预期必须来自独立已发布向量，不能取目标实现输出。

负控制保留全部GHASH/CTR关键词、只把标签掩码换成H；关键词检查仍可能成功，行为向量必须失败。修复定义后升级suite与任务基线，旧结果只对旧字节有效。

先固定接口的明文释放时机、真实API错误和nonce来源；本文件不说明任何特定库自动附带nonce/tag/AAD。
