---
schema: pdca.asset/v1
id: ontology:domain/observability-structured-logging-jsonl-rotation
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/observability-structured-logging-jsonl-rotation/1.0.0
summary: 生产级备份工具结构化日志基线
domain:
- ontology:domain/observability
relations:
  specializes:
  - ontology:domain/observability
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
---


# 生产级备份工具结构化日志基线

## 适用范围

适用于需要保留既有 stderr 文本输出，同时为海量备份、增量扫描和断点续传提供机器可解析观测的单进程工具。该方法解决的是可视化和诊断，不等价于解决 checkpoint 状态的内存线性增长。

## 可复用约束

- 日志 API 应在进程内集中配置，输出入口使用单一互斥锁，保证一条记录不会被并发写入拆开；日志故障不得阻塞备份主流程。
- 文本格式保持 stderr 兼容；JSONL 固定包含 UTC 毫秒时间、level、component、event、message，并补充 pid、线程标识和结构化字段。
- 文件 sink 使用 `O_CLOEXEC|O_NOFOLLOW`、创建权限 `0600`，轮转在同一写锁内完成；轮转和 reopen 失败只报告一次并继续 stderr 输出。
- 字段和消息必须有上限，避免错误路径或恶意路径名造成单条日志无界分配。敏感 token、凭据和原始认证数据不进入事件字段。
- 业务进度解析器与结构化日志必须解耦。文本结构化字段使用带引号的表示，避免 `files=...` 等字段被旧进度扫描器误识别；JSON consumer 使用 JSON parser。
- 关键阶段事件至少覆盖 operation start/complete/failure、增量扫描摘要、skip/send、checkpoint recovery/flush 和提交结果，并用稳定事件名而不是自由文本驱动告警。

## 验证方法

并发、轮转、权限、JSON 解析和敏感字段排除用集成测试验证；Make、CMake TLS ON/OFF 和全回归分别执行。性能必须以至少三次运行的中位数比较，并同时记录 elapsed、CPU、RSS 和缓存占用。日志开销可单独作为吞吐轴，但不能替代 checkpoint 的 RSS 轴；海量状态结构仍需 100k/1M 规模的独立验证。

## 本轮证据边界

T0251 的 100k metadata unchanged-scan JSON 日志中位数开销约 0.9%，且当前 TREE checkpoint 可完成 100k 恢复；但 `TreeCheckpoint::confirmed` 仍是随路径数量增长的内存 map。后续任务必须使用磁盘分页/有序索引验证内存边界，而不能沿用本轮日志开销结果作为证明。
