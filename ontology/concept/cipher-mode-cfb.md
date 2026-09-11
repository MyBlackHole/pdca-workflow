---
schema: pdca.asset/v2
id: ontology:concept/cipher-mode-cfb
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/cipher-mode-cfb/3.1.0
summary: CFB反馈模式；不可与fscrypt CBC-CTS文件名模式混同
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: mode_identity
  desc: 模式身份不能混用
  constraint: CFB反馈段长须明确；CBC-CTS不是CFB别名
  testable_signal: 固定fscrypt v6.12模式清单核对；把CTS当CFB的反例应拒绝
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
  - FSCRYPT_CTS_NOT_CFB
  source_refs:
  - https://www.kernel.org/doc/html/v6.12/filesystems/fscrypt.html
  runtime_validation: not_run
---

# CFB与CBC-CTS不同

全分组CFB的反馈示意为`C0=IV`、`Ci=Pi xor E_K(C_(i-1))`；采用分段CFB时必须另行固定段长、移位和尾部接口规则，不能把此示意当完整实现。

## 已核对的采用边界

[Linux v6.12 fscrypt文档](https://www.kernel.org/doc/html/v6.12/filesystems/fscrypt.html)说明其API的CTS表示CBC-CTS，不是CFB；文件名模式还存在其他选择，本条不声称清单适用于全部内核版本或私有分支。删除旧“fscrypt文件名使用CFB/CTS”的错误归属。

使用某模式需固定真实接口与向量，不能由“适合小块”推导文件系统必然采用。正例：模式ID映射到该版本实际定义；反例：把CFB当CBC-CTS进行互通，应因算法/格式不一致而失败。文件名模式真实运行未在本次执行。
