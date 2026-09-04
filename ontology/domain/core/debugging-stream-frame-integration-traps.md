---
schema: pdca.asset/v1
id: ontology:domain/debugging-stream-frame-integration-traps
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/debugging-stream-frame-integration-traps/1.0.0
summary: 流帧协议集成陷阱：长度前缀、整块 END、序列化对称
domain:
- ontology:domain/debugging
relations:
  specializes:
  - ontology:domain/debugging
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 流帧协议集成陷阱：长度前缀、整块 END、序列化对称

来源：T0212 SCP 业务流式化（2026-08-04），STREAM 帧协议 v2 集成

## 1. 读取裸载荷禁止用带前缀的 getter

### 症状
DATA 帧 payload 无长度前缀（`[subtype u8][payload]`），用 `buf_get_string_direct`
（期待 `[u32 len][data]`）读取时 dlen 错位为 payload 前 4 字节，校验和/解压/写入全错。

### 规则
- 发送 `buf_put_u8(sub) + buf_put(payload, len)`（无前缀）
- 接收 `data = buf_ptr(frm); dlen = buf_len(frm); buf_consume(frm, dlen);`
- `buf_get_string_direct` 只用于真正带 u32 前缀的字段（如 INIT 的 name 区）

## 2. 文件大小恰为块整数倍时最后一块缺 END

### 症状
64MB 文件按 4MB 分块 = 16 整块，`bytes < block_size` 判定永远不成立 →
无 END 标志 → 接收端无限等待 poll 超时。

### 规则（双保险）
- 发送端：内层 read 循环用 `eof` 标志，`bytes < block_size || eof` 才打 END
- 接收端：以元数据中的 total_size 兜底 `recv_bytes >= f_size` 结束，
  END 标志仅作加速提示

## 3. 请求序列化必须与入口解析对称

### 症状
下载 REQUEST 改成帧化发送后，服务端（`rpc_recv` 读原始字节 +
`msg_scp_download_t` 结构映射）解析出空文件名。

### 规则
- 服务端入口是什么字节流，客户端就必须发什么字节流（原始序列化 vs 帧协议）
- 结构体布局（`name_len + 定长区`）与流式 putter（`buf_put_string` 自带长度
  前缀）是两种格式，混用即错位；`name_len` 字段已单独发送时 name 用裸 `buf_put`

## 4. 复用 buffer 读帧前必须 buf_clear

### 症状
`rpc_recv_frame` 用 `buf_reserve` 在现有内容后追加，复用未清空的 buffer
（先发后读同 buffer）导致 body 长度虚增（26 字节帧变 49）。

### 规则
- 每次 `rpc_recv_frame` 前 `buf_clear(msg)`，或每帧新建 buf（服务端模式）

## 5. 测试服务端线程须模拟真实入口

直接调用处理器函数时，`net_buf` 不会自动填充——需先 `rpc_recv` 读请求
填缓冲，与真实分发循环（rpc_recv → ntoh → handler）保持一致。
