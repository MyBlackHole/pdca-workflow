# Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- priority: P1
- source: T0246 Round 60

## 请求解释

“继续下一轮优化”解释为：在已证明显式 `workers=4` 有收益的基础上，继续降低客户端 small-file pack GET 的解码和本地落盘驻留成本。

## 查重

- T0246 已覆盖 writer pool 的错误边界、指标、顺序屏障和初始 worker 矩阵，本任务不重复这些契约。
- 当前没有任务覆盖 small-file pack 的一次性 materialize、重复数据驻留或流式解码。
- `knowledge/benchmark/small-writer-pool-parallelism.md` 明确要求目标设备复测后才考虑改变默认值。

## 事实验证

- `do_get_stream()` 对 `FT_SMALL_FILE_PACK` 先调用 `decode_small_file_pack()`，一次性构造整个 `SmallFilePackItem` vector，再逐项入队。
- 当前队列上限固定为 `max(8, workers*8)`；pack payload、decoded vector 和 queue 可能同时驻留。
- 上一轮基准中 `workers=4` 相对默认路径平均吞吐提升约 36.7%，但结论只覆盖单机、10000 个小文件。

## 推荐下一步

1. 先记录旧实现的吞吐、峰值 RSS、队列峰值和内容正确性基线。
2. 增加 C-style 流式 pack 解码接缝，逐项直接入 writer queue，保留原子发布、metadata、checksum、durability 语义。
3. 用 workers `0/4` 的配对矩阵比较旧实现与流式实现，不自动改变默认值或队列上限。

## 范围控制

保持单任务执行；fast-blob 接收、writer pool 和 benchmark 共享同一外部行为契约，不拆分子 task。
