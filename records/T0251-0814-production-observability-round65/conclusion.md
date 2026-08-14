---
schema: pdca.asset/v1
id: T0251-0814-production-observability-round65
phase: check
source_ids: [logger-unit-integration-style, make-full-regression, cmake-tls-on-regression, cmake-tls-off-regression, event-and-compat-regression, concurrent-rotation-permissions, metadata-100k-log-overhead, checkpoint-100k-recovery, dual-axis-review]
---

## 上下文

本轮目标是为 backupctl/backup-agent 建立生产级结构化日志基线，同时观测海量增量和 TREE checkpoint 的关键阶段；TREE checkpoint 全量确认表的内存重构在 Plan 中明确列为后续独立切片。

## 假设与结果

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| AC-1 Make/CMake TLS ON/OFF、默认 text 兼容 | 通过 | `make-full-regression`, `cmake-tls-on-regression`, `cmake-tls-off-regression` |
| AC-2 CLI 与 JSONL 必需字段 | 通过 | `logger-unit-integration-style` |
| AC-3 并发整行、轮转、重开、0600、失败降级 | 通过 | `concurrent-rotation-permissions`, `logger-unit-integration-style` |
| AC-4 增量/checkpoint/传输/错误事件与 token 隔离 | 通过 | `event-and-compat-regression`, `checkpoint-100k-recovery` |
| AC-5 100k 回归与日志开销 | 通过 | `metadata-100k-log-overhead`, `checkpoint-100k-recovery` |
| AC-6 全量验证与审查 | 通过 | `make-full-regression`, `cmake-tls-on-regression`, `cmake-tls-off-regression`, `dual-axis-review` |

## 分析

100k SQLite 增量扫描三次中位数：日志关闭 unchanged scan 为 0.3132s，JSONL/file sink 为 0.3160s，开销约 0.9%；RSS 中位数约 21.9 MiB，差异低于样本噪声。100k TREE checkpoint 断电恢复通过，跳过 67071 个文件、重送 32929 个文件，尾部截断和源文件变化均安全回退。

主要替代解释已检查：第一次 CMake 回归失败来自 stale build 中旧 text sink，重建后 ON 35/35、OFF 15/15 全部通过；一次 Make 回归因相同旧字段污染进度解析，改为 `key="value"` 后恢复并最终全量通过。代码标准/规范双轴均为 Blocking=0。

## 适用边界

本结论证明日志模块和现有 100k checkpoint 语义可观测、可回归，不证明当前 checkpoint 存储已达到海量内存终态。`TreeCheckpoint::confirmed` 仍是按路径增长的内存表；在更大 namespace 下 RSS 会继续随确认路径增长，必须由下一轮磁盘索引/流式恢复任务处理。

## 下一轮建议

创建跟进任务：将 TREE checkpoint 改为磁盘有序索引或分页 KV 结构，恢复时流式扫描/按目录范围查询，pending 保持有界；保留批次 ACK、尾部截断、generation/fingerprint 校验和源变化安全回退，并用 100k/1M 文件 RSS、恢复吞吐和断电故障注入作为硬验收。日志事件 `checkpoint_recovery`/`checkpoint_flush` 作为该轮观测接口继续复用。
