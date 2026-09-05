---
schema: pdca.asset/v1
id: ontology:domain/core-compress-retry-verify
type: domain
layer: Knowledge
status: active
summary: 压缩失败折半重试 + 重解验证 + 不可压缩传播
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:domain/core-bkey-packed-encoding
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 块压缩写入、算法特化边界、不可压缩标记传播场景
  constraint: 见正文
  testable_signal: "运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查正文引用的 fs/data/compress.c 在仓库中存在且含 attempt_compress 定义"
- name: constraints
  desc: 重试验证前提
  constraint: 见正文
  testable_signal: "通读正文约束节，确认重试收敛条件、验证比对、单向传播三条前提在引用代码中有对应实现"
---

# 压缩失败折半重试 + 重解验证

沉淀自 T0491（内核遗漏扫描）。对照 bcachefs
`fs/data/compress.c`、`fs/data/checksum.c`、`fs/data/extents.c`。

## 核心概念

1. **失败折半重试 + 算法特化**：单 block 直接判不可压缩；
   `attempt_compress` 循环以返回长度作下次输入提示，否则
   按 block 对齐折半重试；LZ4HC 预留 wildCopy 越界字节，
   zstd 头存真实长 + 尾部 bug 余量；成功需压缩后严格更小，
   补零对齐（`bch2_compress`）。
2. **重解验证防错**：`bch2_verify_compress` 重解 memcmp，压缩
   bug 不落地。
3. **不可压缩单向传播**：仅把 none→incompressible 传播，已有
   标记不降级（`bch2_bkey_propagate_incompressible`）。
4. **校验可合并白名单**：仅 none/crc32c/crc64 可合并；以 a.lo
   为 seed，对 b_len 按页喂零页再 xor；窄化三分裂重算，不可
   合并则全量重算（`bch2_checksum_mergeable`、
   `bch2_checksum_merge`、`bch2_rechecksum_bio`）。

## 复用指南

- 压缩重试必须收敛（折半 + 对齐下界），禁止无限重试。
- 压缩输出必须重解验证，算法 bug 用验证拦截而非事后排查。
- 否定性标记（不可压缩）只允许单向传播，禁止回退。
- checksum 合并必须白名单制，nonce/seed 语义先行验证。
