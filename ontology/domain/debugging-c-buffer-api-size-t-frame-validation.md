---
schema: pdca.asset/v1
id: ontology:domain/debugging-c-buffer-api-size-t-frame-validation
type: domain
layer: Knowledge
status: active
summary: C 缓冲区 API 输出参数类型陷阱与帧校验模式
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
  testable_signal: 由领域实践与测试验证
---

# C 缓冲区 API 输出参数类型陷阱与帧校验模式

来源：T0211 rpc 协议/传输层重构（2026-08-03）

## 1. size_t 输出参数必须以 size_t 接收（栈溢出）

### 症状
- 仅在 release（-O2）下崩溃：SIGSEGV，memcpy 源地址异常（如 0x7fff00000000）
- debug 构建完全正常，难以定位

### 根因
```c
size_t nlen;
buf_get_string_direct(msg, &np, (size_t *)&nlen);  // 错误：nlen 声明为 uint32_t
```
- 若 `nlen` 声明为 `uint32_t`，却按 `size_t*`（8 字节）写入 → 栈溢出 4 字节
- 溢出的字节覆盖相邻栈变量（如 np 指针），后续解引用即崩溃
- release 优化下栈布局/寄存器分配不同 → 只在 release 暴露

### 规则
- 任何以 `size_t*` 为输出参数的 API，接收变量必须声明为 `size_t`
- 禁止强制类型转换规避类型不匹配（`(size_t *)&uint32_var` 是明确危险信号）
- 防御：测试构建必须覆盖 release 模式（debug 会掩盖此类溢出）

## 2. 帧/消息校验顺序：先校验后分配

对不可信输入（网络帧），解析顺序固定为：

1. magic 匹配（结构标记，先行失败快）
2. version 匹配（协议演进隔离）
3. total_len 上限检查（如 8MB）——**必须先查上限再分配缓冲区**
4. 字段级再校验（压缩标志组合、subtype 合法值等）

要点：任何内存分配/memcpy 之前必须完成长度上限校验，防止恶意帧触发超大分配或越界拷贝。

## 3. 字节序辅助函数

- `put_u32/put_u16/get_u32/get_u16` 等序列化辅助函数需配套端到端往返测试
- 错误方向（htonl 当 ntohl 用）的典型症状：本机回环测试通过、跨机器失败
- socketpair 测试无法暴露字节序错误，跨机测试或固定魔数帧比对才能发现
