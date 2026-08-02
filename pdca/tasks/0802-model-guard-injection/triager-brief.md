# T0197 Triage Brief

## 分类

- 类型：refactor（测试模型）
- 场景：development
- 父任务：T0196

## 本地源码核验

- 上游 open_bucket 守卫语义：open bucket 由 alloc 路径保证非 free
  （foreground.c free-bucket candidate）；fsck 校验 open bucket 状态
  （check_allocations）；not_rw 语义：background.c:1650-1667
  （bch2_dev_allocator_set_rw rw_devs）、discard.c:357-365
  （bch2_dev_get_ioref(WRITE) 失败）。
- engine-local 对应：`open_bucket`（engine.rs:901，无预校验 insert）、
  `set_device_rw`（engine.rs:924，rw_devs 位图）、
  `verify_guard_invariants`（T0193，open∧free 与 not_rw∧free 非法裁决）。
- 现有模型 `open_bucket_discard_model_protects_open_from_reuse`
  （engine.rs:3511）：op 5/6 用模型影子状态预判 `state != 0` 才 open
  ——模型手写复刻守卫不变量（T0193 conclusion 建议注入实现裁决）。

## 查重

T0193 conclusion 建议「将 open/not_rw 不变量直接注入模型决策（T0189
模型 op 5/6）」；T0196 conclusion 建议「属性测试模型状态机注入守卫
决策（T0193 建议延续）」；无同范围活动任务。

## 推荐

改造模型 op 5/6：删除模型手写守卫预判（`state != 0`），改为无条件
尝试 + 由实现 verify_all / verify_guard_invariants 结果裁决模型期望
（合法态必须 Ok；非法态必须报对应错误名 OpenBucketFree）；新增
set_device_rw op 覆盖 not_rw 维度（not_rw free 桶 → NotRwBucketFree）。
范围外：loom 交错、-f 修复路径。
