# ADR-0020: Small-file pack 流式解码
日期: 2026-08-13
状态: Accepted

## 背景

客户端 TREE GET 收到 `FT_SMALL_FILE_PACK` 后，现有实现先把整个 pack 解码为 `SmallFilePackItem` vector，再将每个 blob 交给有界 writer pool。这样会同时保留 wire payload、decoded item vector、writer queue 和活动任务数据，放大高并发小文件恢复的峰值驻留和分配压力。

## 候选方案

1. 保留一次性 vector 解码，仅调小 writer queue：实现简单，但 pack decoded vector 仍会驻留，且无法消除重复数据复制。
2. 新增显式回调式流式解码，逐项校验并直接入 writer queue：降低驻留和中间容器成本，但需要维护 callback 错误传播和 malformed/trailing 输入语义。

## 决策

选择方案 2。新增 C-style 流式 pack 解码接口，回调上下文显式负责入队；保留旧 vector API 供其他路径使用。协议格式、capability、writer queue 上限、默认 `workers=0` 和顺序屏障不变。旧/新 binary 必须用交替配对 benchmark 比较，不满足耗时和 RSS 门槛时不保留实现改动。

## 影响

成功时降低 decoded pack 的峰值内存和临时对象数量；失败时需要确保 callback 返回错误后停止后续解析并恢复首错。维护成本增加一个解码 API 和单元测试接缝，但 wire compatibility 不变。
