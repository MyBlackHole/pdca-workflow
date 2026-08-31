---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc-zero-copy-transfer
type: domain
layer: Knowledge
status: active
summary: 备份传输：零拷贝 sendfile/splice vs 用户态副本（实测对照）
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
  testable_signal: "检查本文件 tech-poc-zero-copy-transfer 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 备份传输：零拷贝 sendfile/splice vs 用户态副本（实测对照）

## 核心结论

备份数据从磁盘读到网络，零拷贝可避免用户态缓冲拷贝。1GB 回环实测：

| 路径 | 用户态副本 read+write | sendfile | splice |
|------|---------------------|----------|--------|
| 吞吐 | ~2.4 GB/s | 1.6–2.3x | 1.6–2.3x |
| 数据通路 | 内核→用户→内核 | 内核→内核（免用户态） | 内核→pipe→内核 |

## 选型规则

1. **磁盘→网络直通** → `sendfile(fd, socket)`（文件 fd 直发 socket）。
2. **需要多段拼接/回环/需中间处理** → `splice`（fd→pipe→socket，
   两个 splice 调用链）。
3. **回环下收益被内存带宽稀释**（本测仅 1.6–2.3x），真实磁盘+网络场景
   用户态拷贝开销占比大，加速比应更高。
4. 零拷贝前提是数据不需要在用户态改（加密/压缩需先读入——AEAD 加密
   场景建议"加密后再 sendfile"或"内核态 TLS/零拷贝加密"）。

## 适用边界

- 结果基于 tmpfs/回环 socket，未覆盖真实磁盘寻道与网络拥塞。
- splice 需 `SPLICE_F_MOVE` 语义正确性验证；sendfile 要求目标为流式 socket。

## 复用场景

- 备份数据分块读→网络发送的主链路。
- 免去重块的直传路径（哈希命中即直发）。
