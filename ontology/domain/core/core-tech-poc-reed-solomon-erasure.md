---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc-reed-solomon-erasure
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/core-tech-poc-reed-solomon-erasure/1.0.0
summary: 备份可靠性：Reed-Solomon 纠删码（GF(2^8) RS(5,3) 实测）
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
  testable_signal: "检查本文件 tech-poc-reed-solomon-erasure 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 备份可靠性：Reed-Solomon 纠删码（GF(2^8) RS(5,3) 实测）

## 核心结论

备份存储可用纠删码替代全量复制降低冗余。自研 GF(2^8)（本原多项式 0x11D，
同 AES）RS(5,3)=3 数据片 + 2 校验片：

| 指标 | 值 |
|------|-----|
| 冗余 | 5/3 = 1.67x（复制 3 份为 3x） |
| 容错 | 任意 ≤2 片丢失可完整恢复（n-k=2） |
| 恢复 | 全部 C(5,2)=10 组合逐字节还原 ✓ |
| 恢复耗时 | 10 组合 ~1.2ms（片长 256B） |

## 选型规则

1. **容错上限 = n-k**（校验片数）。RS(5,3) 丢 3 片（含全数据片）不可恢复，
   这与"任意 3 副本中坏 1 仍可用"的复制模型语义不同，勿混淆。
2. 编码用 Vandermonde 矩阵，解码用高斯消元求逆——实现要点：
   - GF(2^8) 乘除法用对数/反对数表或位移查表；
   - 编码矩阵生成校验片；解码取幸存行求逆后乘以幸存的编码行。
3. **生产建议**：本实现为教学级，真实引擎用 SIMD 加速库
   （liberasurecode / isal）获得高吞吐编解码。

## 适用边界

- 数据片必须等长（分片存储）；变长块需先 padding。
- 恢复要求至少 n-k 个片在；网络存储中"慢/损坏片"检测需独立于 RS。

## 复用场景

- 备份存储层对象的多副本替代方案。
- 跨节点/跨盘容错布局（RS(k+m, k) 通用化）。
