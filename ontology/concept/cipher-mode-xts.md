---
schema: pdca.asset/v2
id: ontology:concept/cipher-mode-xts
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/cipher-mode-xts/3.1.0
summary: XTS：数据单元tweak与逐块域乘法；固定输入确定且不提供认证
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: tweak
  desc: 区分初始tweak与块号
  constraint: T0=E_K2(i)；Tj=alpha^j·T0；完整块Cj=E_K1(Pj xor Tj) xor Tj
  testable_signal: 固定公开XTS向量和尾块样本；逐块E_K2(i||j)的变体应失败
  evidence_level: behavior
- name: determinism
  desc: 相同输入确定
  constraint: key、数据单元tweak和明文均相同时输出相同；不是AEAD
  testable_signal: 重复固定输入字节相等；不得要求XTS自身检出篡改
  evidence_level: behavior
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
  - XTS_TWEAK
  - XTS_DETERMINISM
  source_refs:
  - https://raw.githubusercontent.com/torvalds/linux/v6.12/crypto/xts.c
  - https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/test/recipes/30-test_evp_data/evpciph_aes_common.txt
  runtime_validation: not_run
---

# XTS：固定位置的tweakable加密

按[Linux v6.12 crypto/xts.c](https://raw.githubusercontent.com/torvalds/linux/v6.12/crypto/xts.c)与[OpenSSL 3.0.16固定测试](https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/test/recipes/30-test_evp_data/evpciph_aes_common.txt)核对本节，不声称私有SM4接口与AES相同。

两个密钥分工：`T0=E_K2(i)`，其中i是约定编码的数据单元标识；后续`Tj=alpha^j·T0`。完整块`Cj=E_K1(Pj xor Tj) xor Tj`；不是每块重新加密`LBA||j`。非整块尾部按XTS ciphertext stealing与前块协作，不能独立零填充。具体实现须固定字节序、数据单元长度限制和密钥长度；AES-128-XTS用两把128位钥，AES-256-XTS用两把256位钥。

同key、同i、同P必然同C；不同位置不是重新随机化机制。XTS不产生认证标签，篡改检出要由另一个明确机制负责。不能把一次解密返回数据当成认证成功。

## 正反例与返工

[密码回归](../../tests/crypto-regression.md)使用固定32字节向量和34字节尾块向量，检查加解密、重复确定性和错误tweak推进。保留正确重复结果；不能为了符合旧版“每次不同”的文字而加入随机化。实际盘格式与API仍需独立互通验证。
