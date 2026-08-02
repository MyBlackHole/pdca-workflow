# T0193 公开守卫断言套件：open/not_rw 不复用与 drop 无泄漏

## 问题陈述

T0189-T0192 累积了三个守卫不变量（open 桶不转 free、not_rw 设备桶不转 free、
drop 无泄漏、worker run 后队列空），但仅散落在各定向/属性测试的局部断言中；
外部调用方无法对任意引擎状态运行这些一致性检查。`verify_bucket_indexes`
（engine.rs:622）只覆盖 alloc/freespace/need_discard 集合一致性，不含守卫
不变量。上游 `bch2_check_allocations`（check.c:1097）是 recovery pass 语义的
engine-local 对应物。

## 目标

将守卫不变量收敛为公开断言 API，供测试与外部调用方复用；内部既有测试切换到
公共断言，验证套件与实现语义单一事实源。

## 验收标准

- [ ] AC-1: 修改前逐段记录 `bch2_check_allocations` 与守卫锚点（open/not_rw/队列空）源码位置。
- [ ] AC-2: 公开 API 断言 open/not_rw 桶不得处于 free 状态（对应 bch2_bucket_is_open_safe 与 dev_get_ioref 语义）。
- [ ] AC-3: 公开 API 断言 drop 无泄漏（查询 open bucket 计数/集合，对应 bch2_open_buckets_stop umount 语义）。
- [ ] AC-4: 公开 API 断言 run_discard_worker 成功后队列空（对应 while-耗尽语义），且不改变 worker 行为。
- [ ] AC-5: 既有 T0189/T0191/T0192 定向与属性测试切换到公共断言，全套测试保持绿。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- 断言 API 为只读（不修改状态），与 verify_bucket_indexes 风格一致。
- 不改变现有公共 API 行为；属性测试的模型断言逐 op 调用公共断言。
- 不实现完整 fsck/GC pass、不引入多设备几何。

## 范围外

完整 fsck、GC pass、多设备拓扑、真实设备 I/O、VFS。

## 备注

前置：T0189/T0191/T0192 已归档，三份 knowledge 均建议本任务。
