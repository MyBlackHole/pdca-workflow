# T0190 discard worker in-flight 去重与重试恢复

## 问题陈述

T0189 已补齐单桶 discard boundary，但尚无 worker 级 in-flight 去重、EEXIST/EAGAIN 返回、
异步完成和重启后重新发现 need_discard 的状态机。

## 目标

依据本地 `fs/alloc/discard.c`，实现 engine-local discard worker 的有限状态、并发去重、
重试与恢复；不实现真实设备 TRIM I/O。

## 验收标准

- [ ] AC-1: 修改前逐段记录 discard in-flight、submit/endio、worker 遍历、going-ro 与 fastpath 源码锚点。
- [ ] AC-2: 同一 bucket 的重复 discard 请求返回 EEXIST 类结果，不产生重复状态转换或重复索引。
- [ ] AC-3: 暂时不可提交返回 EAGAIN 类结果，worker 可重试且不会丢失 need_discard bucket。
- [ ] AC-4: discard 完成、journal commit、generation/free 与 freespace/need_discard 索引保持正确顺序。
- [ ] AC-5: process-style restart 与 fault injection 后，未完成 discard 可重新发现并继续，已完成 discard 不重复执行。
- [ ] AC-6: deterministic、并发/属性、workspace 全量、fmt 和 diff gate 通过；单项不超过一分钟。

## 实现决策

- 用 engine-local 状态与现有 mutex/worker 控制表达 in-flight 集合，避免真实 block I/O 依赖。
- 复用 T0189 的 `discard_bucket` boundary 与 T0188 的 fault/model 测试夹具。
- EEXIST/EAGAIN 仅作为 worker 调度结果，不引入第二套 alloc/backpointer 数据格式。

## 范围外

真实 TRIM/discard bio、设备队列调优、完整 GC/LRU、stripe/EC、VFS、旧格式迁移和多格式兼容。

## 备注

前置：T0189 的 boundary 与 open/live protection 已完成；T0190 只承接 worker 并发与恢复差距。
