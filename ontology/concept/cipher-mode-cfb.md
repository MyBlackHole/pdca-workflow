---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-cfb
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/cipher-mode-cfb/1.0.0
summary: CFB 工作模式（流 C_{i-1} 反馈）解密并行、IV 随机、流无填充、小文件/文件名适配
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: feedback_structure
  desc: CFB 反馈结构（keystream = SM4(K, C_{i-1})，C = P xor keystream）
  constraint: 须含 C_{i-1} 反馈、流模式、解密并行/加密串行
  testable_signal: "运行 grep -q 'C_{i-1}' ontology/concept/cipher-mode-cfb.md && grep -q '解密并行' ontology/concept/cipher-mode-cfb.md"
- name: stream_adaptation
  desc: 流特性与文件名适配（无填充、IV 随机）
  constraint: 须含流无填充、IV 随机、文件名/小块场景
  testable_signal: "运行 grep -q '无填充' ontology/concept/cipher-mode-cfb.md && grep -q 'IV.*随机' ontology/concept/cipher-mode-cfb.md"
---

# CFB 工作模式

`CFB`（`Cipher Feedback`）为流反馈模式，`keystream = SM4(K, C_{i-1})`，`C = P xor keystream`。

## 不变量

- **解密并行**：`keystream` 依赖 `C_{i-1}`，解密可并行，加密串行。
- **流无填充**：密文等长于明文，无 `PKCS#7`。
- **IV 随机**：`C_0 = IV` 需随机，`IV` 重用泄露前缀相等性。
- **文件名适配**：`fscrypt` 文件名 `CFB/CTS` 用，ZFS 数据块不适（串行）。

Source: `NIST SP 800-38A`
