# T0246 Round 60：客户端小文件落盘池背压与并行度优化

## 问题陈述

- **现状**：Round 59 已将服务端 native TLS TREE GET 的大量小文件压缩为
  `FT_SMALL_FILE`/`FT_SMALL_FILE_PACK`，客户端已有可选的
  `SmallLocalWriterPool` 并行落盘路径。
- **目标**：让客户端小文件落盘池的排队、活动任务、完成、背压和失败行为可测；
  修正失败后的控制流；用受控基准验证 worker 数和 durability 模式的实际取舍。
- **差距**：当前池使用固定 `workers * 8` 队列，生产者在满队列上阻塞；错误会清空
  未执行任务并通过共享错误状态传播，但 `enqueue()` 调用点可能继续消费/处理后续
  帧，`drain()` 调用点也可能继续执行硬链接、目录元数据或 TREE_END。上述边界缺少
  独立指标和故障回归。

## 已知信息与 Triage 结论

- 分类：enhancement；场景：development。
- Round 59 已完成服务端小文件 blob/pack 优化，本任务不重复修改 wire format、
  capability 或服务端生产 FSM。
- 现有客户端实现位于 `backupctl` 的 TREE GET 接收路径，`--small-file-workers`
  已是公开参数，默认值为 0。
- 当前可验证的候选方向是池的可观测性、背压契约、错误传播回归和参数化基准；
  是否改变默认 worker 数或队列策略必须由验证结果决定。
- 用户确认：先建立测量和正确性契约，再决定调参/实现优化；保持默认
  `--small-file-workers 0`。
- 用户确认：采用首错 fail-fast、仅通过现有 `--progress` 输出指标，以及分层配对
  benchmark 矩阵。

## 解决方案

客户端继续在一个 TREE GET 接收线程中解码小文件帧，并把 blob 交给有界
`SmallLocalWriterPool`。池保持 `max(8, workers * 8)` 的待执行队列上限；活动任务不
计入该队列上限，但总任务驻留上界为 `workers + max_queue`，并以指标暴露峰值。

writer 首次失败时锁存错误码、errno 和消息，清空尚未开始的队列，禁止新的 enqueue，
并唤醒生产者、消费者和 drain 等待者。接收循环检查 enqueue/drain 结果：一旦失败，
不再消费后续小文件，也不执行依赖已建立 inode 映射的硬链接、目录元数据和 TREE_END
提交动作。已在执行的 worker 允许完成清理，pool 析构前 join 全部线程，最终向调用层
恢复首个错误。

池只增加诊断计数，不增加协议字段或独立控制通道。启用 `--progress` 时输出
`small_writer_workers`、`small_writer_enqueued`、`small_writer_completed`、
`small_writer_peak_queue`、`small_writer_peak_active`、`small_writer_backpressure_waits`
和 `small_writer_failed`；未启用 writer pool 时这些字段保持零或明确表示 disabled。

基准先运行 `workers=0/1/2/4/8`、checksum 关闭、`durability=none` 的交替配对样本；
再对 `workers=0/4` 增加 checksum 开启和 `durability=strict` 的聚焦样本。基准报告
每对耗时、文件速率、最小/最大值和配对均值，不以单次 loopback 数值宣称普遍收益。

## 信息缺口

- 不同 worker 数在无 checksum、checksum、`fsync` 和 `syncfs` 下的吞吐与尾延迟。
- 队列满时的最大内存/排队上界是否与帧大小和 worker 数相符。
- 写入失败、校验失败、目标冲突时，已完成任务、未执行任务和后续元数据屏障的行为。
- 指标输出的字段是否足以解释队列峰值、背压等待和失败传播。
- 在本机噪声下，worker 数是否存在稳定的收益点，还是仅能证明不回归。

## 用户故事

1. 作为大量小文件的 GET 用户，我希望启用 writer pool 时能看到队列和完成状态，
   以便判断并行度是否真正生效。
2. 作为可靠性维护者，我希望任一小文件落盘失败后传输尽快停止并保留首个错误，
   以便避免后续硬链接或目录提交建立在不完整树上。
3. 作为性能维护者，我希望用交替配对基准比较 worker 数、checksum 和 durability，
   以便基于可复现证据选择参数。

## 初步范围

- 客户端小文件 writer pool 的状态指标、背压边界和错误/停止状态。
- 小文件树 GET 的确定性集成回归与可重复 benchmark。
- 保留现有协议、文件发布原子性、目录元数据顺序、硬链接语义和默认关闭池的兼容行为。

## 实现决策

- 修改客户端 TREE GET 接收路径与 `SmallLocalWriterPool` 的状态传播，不修改服务端
  small-file wire format、capability 或生产 FSM。
- `enqueue` 和 `drain` 使用可判定的成功/失败结果；调用方在每个小文件帧、硬链接和
  TREE_END 屏障后检查结果。
- 计数器在 pool mutex 保护下更新和快照，避免为诊断指标新增跨线程原子状态；错误
  信息只锁存首个失败。
- 保留固定 `max(8, workers * 8)` 队列和默认 `workers=0`，本轮只用 benchmark 产生
  调参证据，不自动改变默认行为。
- 任何已完成的小文件仍保持原子 partial-file publish、元数据应用和 fsync 语义；
  普通大文件 regular FSM 不进入 writer pool。

## 测试决策

- 集成测试通过真实 TLS TREE GET，覆盖 packed small files、single blob、regular stream、
  hard-link ordering、writer metrics 和冲突目标失败路径。
- 失败路径以可构造的只读目标根触发，断言命令非零退出且不会挂起；不依赖人工
  杀线程或不可重复的磁盘故障。
- benchmark 使用进程级交替配对，至少四对样本；报告配对均值和 min/max，避免单次
  loopback 样本成为硬阈值。
- 保留 workers=0 路径作为同步基线，确保新增池逻辑不会改变默认行为。

## Seam 分析

### 测试接缝

- 测试边界是 backupctl 的真实 TLS TREE GET 命令到本地目标文件树的外部行为。
- 集成测试验证文件内容、数量、硬链接 inode、错误退出和 progress 字段；benchmark
  验证可重复的耗时/文件速率输出。
- 外部依赖使用测试脚本启动临时 `backup-agent`、临时 TLS 证书和临时源/目标目录；
  不 mock 文件系统、TLS 或线程池。

### 声明的测试接缝

- seam: tests/tls_tree_small_pack_integration.sh -> backupctl
- seam: tests/benchmark_tree.sh -> backupctl

### 验收可测性

- 每个验收项均由集成断言、progress 字段约束、benchmark 输出或构建/回归命令给出
  明确 pass/fail 信号。
- 错误路径使用固定目标冲突构造，顺序路径使用固定 hard-link 源树构造。
- 端到端测试覆盖传输协议、接收循环、线程池和目标文件发布；指标与 benchmark 不
  作为正确性唯一证据。

## 验收标准

- [ ] AC-1: `tests/tls_tree_small_pack_integration.sh` 在 `--small-file-workers 0` 和 `4` 两种客户端 GET 配置下均成功恢复 3,000 个 packed 小文件、blob 文件和 regular stream 文件，内容和文件数量一致。
- [ ] AC-2: writer pool 启用且 `--progress` 时输出 `small_writer_workers`、`small_writer_enqueued`、`small_writer_completed`、`small_writer_peak_queue`、`small_writer_peak_active`、`small_writer_backpressure_waits`、`small_writer_failed`；其中 completed 不大于 enqueued，peak_active 不大于 workers，peak_queue 不大于 `max(8, workers*8)`。
- [ ] AC-3: hard-link 源树在 writer pool 启用时恢复后，原文件与 hard-link 的 inode 相同；目录元数据应用和 TREE_END 提交发生在 writer pool drain 成功之后，现有 hard-link/metadata 回归不失败。
- [ ] AC-4: 将小文件目标根设为只读使 writer 失败时，GET 命令在有界时间内非零退出，保留首个落盘错误，不继续执行后续硬链接、目录元数据或 TREE_END 提交，且所有已创建 writer 线程均被回收。
- [ ] AC-5: `tests/benchmark_tree.sh` 支持并输出交替配对的 `workers=0/1/2/4/8` 无 checksum、`durability=none` 基线，以及 `workers=0/4` 的 checksum/`durability=strict` 聚焦样本；每组至少四对并报告配对均值与 min/max。
- [ ] AC-6: 默认 `--small-file-workers 0` 的 GET 行为、协议能力协商、普通大文件 regular FSM 和现有 TLS tree integration 回归不变。
- [ ] AC-7: GNU Make TLS=1/TLS=0 与 CMake TLS=OFF/ON 的相关构建和测试通过，且无新增编译警告。

## 范围外

- 不新增线程模型、Reactor、协议帧或 capability。
- 不在没有 A/B 证据的情况下修改 `--small-file-workers` 默认值。
- 不将普通大文件 regular FSM 改造成小文件池路径。

## 备注

- 关键错误边界记录于 ADR-0019。
- 相关历史基线：docs/ROUND59_REVIEW.md；现有小文件回归：tests/tls_tree_small_pack_integration.sh。
