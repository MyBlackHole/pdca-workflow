# T0197 属性测试模型状态机注入守卫决策

## 问题陈述

`open_bucket_discard_model_protects_open_from_reuse`（engine.rs:3511）
的 op 5/6 用模型影子状态预判 `if state[index] != 0` 才执行 open_bucket
——模型手写复刻了实现的守卫不变量（open∧free 非法）。当守卫语义在
实现中演进（如新增 not_rw 维度）时，模型规则与实现重复、易漂移。
T0193 conclusion 建议将 open/not_rw 不变量直接注入模型决策，由实现
裁决而非模型预判。

## 目标

模型 op 5/6 删除手写守卫预判：无条件尝试 open/close，由实现
verify_all / verify_guard_invariants 结果驱动模型期望——合法操作必须
Ok，非法操作必须报对应错误名（OpenBucketFree / NotRwBucketFree）。
新增 set_device_rw 操作覆盖 not_rw 维度。模型从"预判合法"变为
"探索含非法在内的操作并用实现裁决"。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点（open bucket 守卫语义、not_rw
      rw_devs、fsck 校验 open bucket 状态）与现有模型 op 5/6 结构。
- [ ] AC-2: 模型 op 5/6 删除手写守卫预判；open 后模型期望由实现裁决：
      合法态 verify_all Ok，非法态（open∧free）报 OpenBucketFree。
- [ ] AC-3: 新增 set_device_rw op：not_rw 维度下模型操作合法/非法
      期望与实现裁决一致（not_rw∧free → NotRwBucketFree；not_rw 时
      allocate/reclaim 失败语义保留）。
- [ ] AC-4: 随机序列（含非法操作路径）全程模型状态与引擎实际状态
      一致（alloc 树投影、open/queued 影子状态）。
- [ ] AC-5: 库 API 不变（仅测试模型改造）；verify_all /
      verify_guard_invariants 行为不变。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- 只改测试模型（engine.rs tests 模块），生产代码零改动。
- 模型维护"预期非法"标志：open free 桶 → 期望 verify_all 报
  OpenBucketFree；not_rw free 桶 → NotRwBucketFree；其余操作非法态
  （reclaim open 桶 -16、allocate not_rw -1）已有覆盖保留。
- 模型状态仍从 alloc 树投影（flush-reopen op 既有逻辑），open/queued
  影子状态由实现结果驱动（open 返回 Ok → open=true）。

## 范围外

loom 风格并发交错、-f force 修复路径、真实设备 I/O、
新增公开 API。

## 备注

前置：T0189（模型 op 5/6 引入）、T0193（守卫断言）、T0194
（verify_all 聚合）、T0196（worker 检查点）已归档。
