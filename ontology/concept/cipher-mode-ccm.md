---
schema: pdca.asset/v2
id: ontology:concept/cipher-mode-ccm
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-12'
owl_versionIRI: http://pdca.local/ontology/cipher-mode-ccm/3.1.0
summary: CCM：规定格式化与补零，M/L显式，区分CBC-MAC值与输出标签
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
  - ontology:concept/cipher-mode-gcm
attributes:
- name: format_and_tag
  desc: CCM内部格式化
  constraint: M取4/6/8/10/12/14/16字节，L为2至8；禁止PKCS#7替代内部补零；输出标签需S0掩码
  testable_signal: RFC3610向量1及0/1/15/16/17字节边界；PKCS7或遗漏掩码变体必须失败
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
  - CCM_FORMAT
  - CCM_TAG
  - CCM_M_L
  source_refs:
  - https://www.rfc-editor.org/rfc/rfc3610.txt
  runtime_validation: not_run
---

# CCM：CBC-MAC与CTR的组合

范围固定[RFC 3610 §2与向量1](https://www.rfc-editor.org/rfc/rfc3610.txt)。nonce长度为15−L字节，L为2…8；M为4/6/8/10/12/14/16字节。nonce在同key下须唯一，消息长度必须能用L字节表示。

## 格式化

`B0=flags||nonce||[len(P)]_L`，长度大端；flags含AAD是否存在、(M−2)/2及L−1。非空AAD先编码长度：小于0xff00用2字节，否则按RFC采用0xfffe+4字节或0xffff+8字节；空AAD不添加该段。AAD编码段与P分别在必要时补零至16字节，整块不额外加块；不是PKCS#7。

对B0及格式化块计算CBC-MAC，取前M字节为T；计数器0生成S0，输出认证字段为`U=T xor first_M(S0)`。P由从1开始的计数器流加密。解密认证失败不能交付明文。

## 单元测试

[密码回归](../../tests/crypto-regression.md)固定8字节标签的RFC向量1，另对空/短/整块/跨块消息与M/L边界核对。PKCS#7替换补零、遗漏S0掩码、错误M/L或篡改认证数据都不能被视为正确结果。参考函数的受支持范围须显式写出；工具错误不等于认证正确拒绝。

CCM不是与GCM互通的替换格式。某个项目采用哪种模式和参数，需要自己的协议；本资料不声称两者性能有不依赖环境的排序。
