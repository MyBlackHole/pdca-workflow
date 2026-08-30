---
schema: pdca.asset/v1
id: ontology:domain/benchmark-small-pack-streaming-decode
type: domain
layer: Knowledge
status: active
summary: Small-file Pack 流式解码
domain:
- ontology:domain/benchmark
relations:
  specializes:
  - ontology:domain/benchmark
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# Small-file Pack 流式解码

## 模式

当协议帧包含多个小文件时，不要先把整个 pack materialize 成 item vector 再交给有界 writer queue。更稳妥的边界是：逐项校验 flags、length、blob metadata 和 data size，通过显式 callback 立即移交当前 item；callback 失败则停止解析并保留首错。

这样可以避免 wire payload、decoded vector、writer queue 和活动任务同时驻留。保留旧 vector API 作为兼容包装时，其他调用方可以渐进迁移，而客户端热路径使用流式 API。

## 验证方法

- unit：合法顺序、空包、截断、长度越界、非法 blob、trailing bytes 和 callback fail-fast。
- integration：真实 TLS TREE GET 验证内容、hardlink、metadata 屏障、失败边界和线程回收。
- benchmark：旧/新 binary 交替配对，报告耗时、files/s、峰值 RSS 和 queue peak；若耗时回退超过 5% 或 RSS 不下降，则不保留优化。

## Round 61 结果

10000 个小文件、四对样本下，workers=0 耗时增加约 1.9% 但峰值 RSS 下降约 2.1%；workers=4 耗时基本持平且 RSS 下降约 1.0%；strict+checksum workers=4 耗时下降约 4.5%，RSS 下降约 2.8%。结论是保留流式解码，但继续保持默认 `workers=0` 和既有协议。
