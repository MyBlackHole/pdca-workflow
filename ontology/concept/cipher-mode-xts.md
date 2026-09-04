---
schema: pdca.asset/v1
id: ontology:concept/cipher-mode-xts
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/cipher-mode-xts/1.0.0
summary: XTS 工作模式（tweak=LBA 窃取法）盘加密专用、均并行、无额外存储、需双密钥
relations:
  specializes:
  - ontology:concept/cipher-mode
  relates_to:
  - ontology:domain/encryption-modes
attributes:
- name: tweak_structure
  desc: XTS 的 tweak 结构（C = P xor E(K2,tweak) → SM4(K1) → xor E(K2,tweak)，tweak=LBA）
  constraint: 须含 tweak=LBA/扇区号、双密钥 K1/K2、窃取法处理尾块
  testable_signal: "运行 grep -q 'tweak' ontology/concept/cipher-mode-xts.md && grep -q 'LBA' ontology/concept/cipher-mode-xts.md"
- name: disk_adaptation
  desc: 盘加密适配（无额外存储、随机访问、需双密钥）
  constraint: 须含盘加密专用、无额外存储、随机访问、需双密钥 256b
  testable_signal: "运行 grep -q '盘加密' ontology/concept/cipher-mode-xts.md && grep -q '双密钥' ontology/concept/cipher-mode-xts.md"
---

# XTS 工作模式

`XTS`（`XEX-based Tweaked-codebook with ciphertext Stealing`）为 `IEEE P1619` 标准化的盘加密专用模式。

## 结构

`C = P xor E(K2, tweak) → SM4(K1) → xor E(K2, tweak)`，`tweak = LBA（扇区号）|| blockIndex`，`K1/K2` 双密钥 `256b`，尾块不足 `128b` 时窃取法免填充。

## 不变量

- **均并行**：每扇区独立 `tweak`，可随机访问。
- **无额外存储**：密文等长于明文，无 `tag` 膨胀（对比 `GCM` 的 `16B tag`）。
- **盘加密专用**：同扇区同明文不同密文（`tweak` 隔离），`fscrypt XTS` 用。
- **需双密钥**：`K1` 加密 `K2` 调 `tweak`，实现复杂。

Source: `IEEE P1619` + `NIST SP 800-38E`
