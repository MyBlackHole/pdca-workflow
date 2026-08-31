---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc-bloom-filter-dedup
type: domain
layer: Knowledge
status: active
summary: 备份去重索引：布隆过滤器 vs 精确哈希表（实测对照）
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
  testable_signal: "检查本文件 tech-poc-bloom-filter-dedup 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 备份去重索引：布隆过滤器 vs 精确哈希表（实测对照）

## 核心结论

备份去重需"某块指纹是否已存在"的索引。布隆过滤器以假阳率为代价换取内存
（实测 N=1M、m/n=8、k=6）：

| 指标 | 布隆位数组 | 精确哈希表 |
|------|-----------|-----------|
| 内存 | 1 MB | 61 MB（每条 64B 指纹） |
| 假阴性 | 0（必无） | 0 |
| 假阳率 | ~2.16%（实测=理论） | 0 |
| 插入 | 75M/s 量级 | — |

## 选型规则

1. **内存是瓶颈** → 布隆。m/n=8 时假阳率 ~2.16%（理论 `(1-e^(-kn/m))^k`，
   最优 k=m/n·ln2≈5.5，取 6）。
2. **假阳率可容忍**（命中后再查精确索引二次确认）→ 布隆做第一道过滤，
   精确表做第二道。假阳性代价仅一次磁盘确认，可接受。
3. **双哈希派生**（`pos_i=(h1+i·h2)%m`，Kirsch-Mitzenmacher）足够，
   但非严格独立会使实测假阳率略高于理论（本测 2.1602% vs 2.1577%），
   断言容差按 1.5x 处理。

## 适用边界

- 结果基于 1M 元素、20M 次探测；假阳率为统计量，样本越大越收敛。
- 若需"零假阳且省内存"，可考虑 Cuckoo filter 或布隆+精确表级联。

## 复用场景

- 备份客户端/服务端去重索引的内存态实现。
- 高吞吐指纹查重的第一道过滤。
