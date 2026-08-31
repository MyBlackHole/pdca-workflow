---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc-hash-selection
type: domain
layer: Knowledge
status: active
summary: 备份引擎哈希选型：XXH3 / BLAKE3 / SHA-256（实测对照）
domain:
- ontology:domain/core-tech-poc
relations:
  specializes:
  - ontology:domain/core-tech-poc
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件 tech-poc-hash-selection 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 备份引擎哈希选型：XXH3 / BLAKE3 / SHA-256（实测对照）

## 核心结论

备份链路哈希有两处用途：**分块指纹（去重索引）** 与 **数据完整性校验**，
对速度与安全要求不同。本机（x86-64，SHA-NI 加速）1GB 实测：

| 哈希 | 吞吐 | 定位 | 用例 |
|------|------|------|------|
| XXH3 | ~13 GB/s | 非密码学、极速 | 去重指纹、布隆索引、滚动哈希种子 |
| BLAKE3 | ~3.3 GB/s | 密码学、快、无密钥 | 内容寻址指纹、完整性（信任场景） |
| SHA-256 | ~1.85 GB/s | 密码学、最保守 | 安全要求最高、外部兼容 |

## 选型规则

1. **去重/索引层**（不进审计、非安全边界）→ XXH3。~7x SHA-256，
   128-bit 碰撞概率对备份规模可接受。
2. **完整性/内容寻址**（安全边界）→ BLAKE3（比 SHA-256 快 ~1.8x，
   且并行化可扩展），或按合规要求 SHA-256。
3. 64B 短块场景 BLAKE3 官方向量：`BLAKE3("")=af1349...3262`、
   `BLAKE3("abc")=6437b3...9d85`，可作实现自测锚点。

## 适用边界

- 绝对吞吐因硬件而异（AES-NI/SHA-NI 有无差异大），相对关系稳定。
- libblake3/libxxhash 为非系统默认库，需显式链接 `-lblake3 -lxxhash`。

## 复用场景

- 备份去重引擎的块指纹计算。
- 备份元数据内容寻址（CAS）存储。
- 传输完整性校验（AEAD 已覆盖时无需再独立校验）。
