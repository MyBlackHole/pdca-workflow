# T0247 Round 61：小文件 pack 流式解码与落盘驻留优化

## 问题陈述

- **现状**：Round 60 已实现有界 `SmallLocalWriterPool`，显式 `workers=4` 在当前主机上较默认路径有收益。客户端收到 `FT_SMALL_FILE_PACK` 后，`decode_small_file_pack()` 会先把整个 pack 解码成 `SmallFilePackItem` vector，再逐项入队。
- **目标**：降低 pack 解码阶段的临时对象、数据拷贝和峰值内存驻留，同时保持 writer queue 背压、首错 fail-fast、hardlink/目录/TREE_END 顺序和 wire protocol 不变。
- **差距**：pack payload、完整 decoded vector、writer queue 和活动 worker 数据可能同时驻留；当前没有旧实现与流式实现的峰值 RSS 和吞吐对照。

## 解决方案

新增 C-style 流式 pack 解码接口：校验 pack header、flags、item length、blob metadata、blob data size 和 trailing bytes 后，按 wire 顺序逐项调用显式回调。客户端 GET 接收路径直接把每个 blob 移交给 `SmallLocalWriterPool::enqueue()`，不再 materialize 整个 pack item vector。

流式接口只改变本地解码和入队方式，不改变 `FT_SMALL_FILE_PACK` 格式、capability、checksum、durability、原子 partial-file publish 或默认 `--small-file-workers 0`。既有 vector 解码接口保留给其他调用方，避免扩大本轮兼容面。

基准先构建旧实现和优化实现，使用同一源树、同一 agent 参数和交替配对 GET，记录 workers=0/4 下的耗时、files/s、峰值 RSS、`small_writer_peak_queue` 与正确性；strict+checksum 再做聚焦配对。若优化实现平均耗时超过旧实现 5% 或峰值 RSS 不下降，则不保留实现改动，记录为测量结论。

## Seam 分析

### 测试接缝

- 真实 TLS TREE GET 接缝验证 pack 解码、writer pool、目标文件发布和错误传播。
- 单元接缝验证合法 pack 的顺序回调及 malformed/trailing pack 拒绝。
- benchmark 接缝在旧/新 binary 间交替运行同一外部命令，收集时间和 RSS，不 mock 文件系统、TLS 或线程池。

### 声明的测试接缝

- seam: tests/tls_tree_small_pack_integration.sh -> backupctl
- seam: tests/benchmark_tree.sh -> backupctl

### 验收可测性

- 每个验收项均有明确的集成断言、单元返回值、benchmark summary 或构建/回归退出码。
- malformed pack、trailing bytes 和 item length 越界可由单元输入确定性构造。
- 旧/新 binary 对照使用相同 10000-file tree 和至少四对交替样本；性能门槛不以单次样本判定。

## 用户故事

1. 作为大量小文件 GET 用户，我希望 pack 解码不会额外复制并长期持有整个包，以便降低峰值内存和分配压力。
2. 作为可靠性维护者，我希望流式解码仍逐项保持协议顺序，并在 malformed pack 时立即失败，不让部分数据越过错误边界。
3. 作为性能维护者，我希望旧/新实现有可复核的配对耗时、RSS 和正确性证据，以便只保留真实收益。

## 实现决策

- 增加显式回调式流式 pack 解码接口，回调上下文负责把 `SmallFileBlob` 和 prechecked 标志转交 writer pool。
- 解码器在回调前完成单项 blob 完整性校验；回调失败立即停止后续解析并恢复首个错误。
- 保留现有 `decode_small_file_pack()` vector API，减少对 agent PUT/native GET 其他路径的影响。
- 不调整 writer queue 上限，不新增协议字段，不改变默认 workers 或自动调参行为。

## 测试决策

- 集成测试覆盖 workers=0/4、pack/blob/regular、hardlink、metrics 和 read-only failure path。
- 单元测试覆盖 pack item 顺序、flags、空/截断/尾随 malformed 输入和 callback fail-fast。
- benchmark 输出 paired line、mean/min/max、files/s、RSS 和 queue peak；旧 binary 与新 binary 使用独立临时目录。
- GNU Make TLS=0/1、CMake TLS OFF/ON 和既有 tree/FSM 回归继续作为兼容门禁。

## 验收标准

- [ ] AC-1: TLS small-pack integration 在 workers=0/4 下恢复全部 packed files、single blob、regular stream 和 hardlink，内容、数量和 inode 均正确，既有 failure path 仍非零退出且不创建后续 hardlink。
- [ ] AC-2: 流式解码单元或确定性测试按 pack wire 顺序回调每个 item；合法 flags/data 保持一致，空 pack、截断 item、越界 length、非法 blob 和 trailing bytes 均失败且不会回调后续 item。
- [ ] AC-3: workers=4 的 progress 指标仍满足 completed<=enqueued、peak_active<=workers、peak_queue<=max(8,workers*8)，且流式路径错误时首错 fail-fast、活动 worker 可回收。
- [ ] AC-4: 旧实现与流式实现使用相同 10000-file tree 完成至少四对交替 benchmark；输出耗时、files/s、峰值 RSS、queue peak 和 strict+checksum 聚焦结果，流式实现平均耗时不劣化超过 5%，峰值 RSS 不高于旧实现。
- [ ] AC-5: 默认 workers=0、wire protocol/capability、checksum/durability、普通大文件 regular FSM、hardlink/metadata/TREE_END 顺序和既有 TLS tree integration 回归不变。
- [ ] AC-6: GNU Make TLS=1/TLS=0 与 CMake TLS=OFF/ON 相关构建和测试通过，且无新增编译警告。

## 范围外

- 不改变 `--small-file-workers` 默认值，不自动选择 worker 数。
- 不修改 small-file pack wire format、capability 或服务端 native TREE FSM。
- 不调整 writer queue 上限，不引入新线程模型、Reactor 或协议 metrics 通道。
- 不对普通大文件 regular stream 做 read pipeline 或 sendfile 优化。

## 备注

- 旧实现基线必须在 Do 阶段修改前固化；若优化门槛不满足，Act 阶段记录 no-op/revert 结论。
- 适用范围仍受本机文件系统、CPU、page cache 和系统负载影响；不能仅凭 loopback 单次结果改变默认策略。
