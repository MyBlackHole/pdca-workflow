---
schema: pdca.asset/v1
id: T0247-0813-small-writer-pool-round61
phase: check
source_ids: [directed-regressions, benchmark-old-new, build-matrix, ctest-tls-off, ctest-tls-on, style-check, review-report]
---

## 上下文

本轮将客户端 `FT_SMALL_FILE_PACK` 接收从“完整 vector materialize 后入队”改为逐项流式解码并直接交给既有 writer pool，目标是降低临时对象和峰值驻留，不改变协议、默认 workers=0、队列上限或顺序屏障。

## 假设与结果

假设成立，AC-1 至 AC-6 全部满足。

- 新增 unit 覆盖 pack 顺序、flags、空包、截断、长度越界、非法 blob、trailing bytes 和 callback fail-fast。
- TLS small-pack 集成、hardlink、失败边界和既有 tree/FSM 回归通过。
- Make TLS=1 完整测试通过；TLS=0 构建通过；CMake TLS OFF `14/14`、TLS ON `34/34` 串行通过。
- 旧提交 `4f3aa8a` 与新实现使用 10000 文件、4 对交替样本比较：
  - workers=0：`0.445369s -> 0.453728s`，耗时增加约 1.9%，低于 5% 门槛；峰值 RSS `7704 -> 7544 KiB`，下降约 2.1%。
  - workers=4：`0.317211s -> 0.317269s`，基本持平；峰值 RSS `7572 -> 7496 KiB`，下降约 1.0%。
  - strict+checksum workers=4：`0.227387s -> 0.217250s`，耗时下降约 4.5%；峰值 RSS `9944 -> 9664 KiB`，下降约 2.8%。

## 分析

流式接口在每个 callback 前校验 item length、blob metadata 和 data size，callback 失败立即停止解析并恢复首错。客户端 callback 直接移动当前 blob 到 pool，避免完整 decoded vector 与 queue 同时驻留；既有 vector API 复用流式接口，其他调用方保持兼容。

收益主要体现在峰值 RSS 和高成本 checksum/durability 场景；无校验 workers=0 存在小幅耗时回退但在门槛内，workers=4 常规场景无显著变化。因此不改变默认 `--small-file-workers 0`，也不自动调高并行度。

代码审查双轴为 Blocking=0；未发现越界、UAF、线程生命周期、协议兼容或 C-style 规范问题。

## 适用边界

- 性能数据来自当前主机、10000 个小文件和四对样本；不能外推到所有文件系统。
- RSS 依赖 GNU `/usr/bin/time` 的子进程峰值统计；缺少该工具的环境只能复测耗时和正确性。
- 流式解码降低 decoded pack 的驻留，但单个 frame payload 仍需在当前 frame 生命周期内保留。

## 下一轮建议

保留流式解码实现，默认 workers=0 不变；在目标存储设备复跑相同旧/新配对矩阵。若后续仍需优化，应优先测量 `recv_small_blob` 的 openat/metadata/fsync 成本，而不是继续扩大队列或线程数。
