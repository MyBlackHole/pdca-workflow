# T0193 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0192

## 本地源码核验

- `fs/btree/check.c:1097-1160`：`bch2_check_allocations` 是 recovery pass，
  遍历全部桶引用重算 alloc/accounting 一致性，失败由 recovery 流程上报——
  subvol `verify_bucket_indexes`（engine.rs:622）已是其 engine-local 对应。
- 断言套件的语义来源分布在 T0189/T0191/T0192 已对齐锚点：
  `bch2_bucket_is_open_safe`（discard.c:344-347/433-436）→ open 桶不得转 free；
  `bch2_dev_get_ioref(WRITE)`（discard.c:357-365）→ not_rw 设备桶不得转 free；
  `bch2_open_buckets_stop`（fs.c:324）→ drop 时无泄漏；
  `bch2_do_discards_fast_work` while 耗尽（discard.c:605-633）→ run 后队列空。

## 查重

T0189/T0191/T0192 三份 knowledge 均记录「不变量提升为公开断言工具」建议，
尚未实现；`verify_bucket_indexes` 已公开但只覆盖 alloc/freespace/need_discard
集合一致性，不覆盖 open/not_rw/队列空守卫不变量。无同范围活动任务。

## 推荐

新增公开断言 API 将三个守卫不变量收敛为一套可复用断言：
① open/not_rw 桶不得处于 free 状态；② drop 后引擎无 open 泄漏（查询）；
③ run_discard_worker 成功后队列空。内部测试（T0189/T0191/T0192 定向与属性
测试）切换到公共断言，外部调用方可对任意引擎状态运行。
