---
schema: pdca.asset/v1
id: ontology:domain/core-tech-poc-frame-multiplexing
type: domain
layer: Knowledge
status: active
summary: 备份传输：单连接多流帧复用（16B 帧头 + 累积缓冲拆帧器）
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
  testable_signal: "检查本文件 tech-poc-frame-multiplexing 相关章节的定义完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空"
---


# 备份传输：单连接多流帧复用（16B 帧头 + 累积缓冲拆帧器）

## 核心结论

备份控制面/数据面常需"一个 TCP 连接承载多个逻辑流"（多通道并行、多任务
并发）。实测自研帧协议：

| 项 | 值 |
|----|-----|
| 帧头 | magic(4)+len(4)+sid(2)+type(1)+flags(1)+crc(4) = 16B |
| 多路复用 | 4 逻辑流 × 2000 帧单连接交织 ✓ 流隔离/顺序完整 |
| 粘包/半包 | 1–5B 随机切片全重组正确 |
| 篡改 | 帧头 sid 翻转 → CRC 检出 |
| 流终止 | EOF 帧逐流送达断言 |

## 选型规则

1. **拆帧器用累积缓冲 + 长度前缀**：读到 `len` 字节才剥出一帧，剩余留在缓冲
   继续——正确处理粘包与半包。
2. **帧头 CRC 必验**：CRC 防随机位翻转/错位（非防恶意，恶意需 AEAD）。
3. **实现关键坑**：`memmove` 压缩缓冲后返回帧内 payload 指针会指向被挪动的
   区域——须先把 payload 拷到调用者缓冲再 memmove。
4. type 区分数据帧/EOF 帧，EOF 使流语义显式（半关闭语义在单 socket 上
   无法用 FIN 区分各流）。

## 适用边界

- 帧头开销 16B/帧，小块传输会放大开销——按数据规模权衡帧大小。
- CRC32 为检测非防护；高安全场景叠加 AEAD 加密层。

## 复用场景

- 备份客户端-服务端单连接多通道复用。
- 分块并行传输时的流式拆包。
