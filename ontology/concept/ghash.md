---
schema: pdca.asset/v2
id: ontology:concept/ghash
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-07
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/ghash/3.1.0
summary: GHASH递推与GCM输入格式分离；不以简化概率式证明实现安全
relations:
  relates_to:
  - ontology:concept/cipher-mode-gcm
  - ontology:domain/encryption-modes
  specializes:
  - ontology:concept/entity
attributes:
- name: recurrence
  desc: 有限域递推
  constraint: Y0=0；Yi=(Y_(i-1) xor Xi)·H，128位分组；GCM另行构造含长度的输入
  testable_signal: 对GCM固定向量核对域乘法/bit顺序/长度格式，错误长度或错掩码须被识别
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
  - GHASH_RECURRENCE
  - GCM_FORMAT_BOUNDARY
  source_refs:
  - https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
  runtime_validation: not_run
---

# GHASH与GCM标签不是同一个函数

按[SP 800-38D（2007）§6.3–6.4/7.1](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)，GHASH对完整128位分组递推：`Y0=0`，`Yi=(Y_(i-1) xor Xi)·H`。域为GF(2^128)，约化多项式为`x^128+x^7+x^2+x+1`；bit串映射必须与标准一致。

GCM负责先格式化AAD、密文、补零和bit长度，再调用GHASH；GHASH本身不会自动推断AAD边界或追加长度。GCM标签还需要`E_K(J0)`掩码与所选截断，见[cipher-mode-gcm](cipher-mode-gcm.md)。

旧版把通用认证界简化为一个固定概率公式、把所有nonce重用样本称作可直接解线性方程、把一次乘法指令称作完整域乘法，均不再作为本节点约束。安全边界和加速策略需要各自前提与来源，不能靠术语生成验收。

单元测试采用[密码回归](../../tests/crypto-regression.md)：正确构造匹配公开向量；省略长度、交换AAD/C或用H当掩码都应违反对应向量。参考测试只证明这些样本，不证明任意实现安全。
