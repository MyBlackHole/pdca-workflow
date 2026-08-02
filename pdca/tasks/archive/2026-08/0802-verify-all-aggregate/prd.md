# T0194 verify_all 聚合入口：合并全部一致性校验

## 问题陈述

engine 现有四个一致性校验 API（verify 拓扑 / verify_derived_state 指针集 /
verify_bucket_indexes 桶索引 / verify_guard_invariants 守卫），测试中 29 处
逐点调用，调用方需自行组合且易遗漏。上游 recovery 以 pass 序列按依赖序
批量执行（passes_format.h:55-98，recovery.c pass 驱动），engine-local 缺
少对应的批量入口。

## 目标

新增 `verify_all()` 单入口，按固定顺序执行全部四个校验，保留首个错误
（`?:` 模式：全部执行、首个错误优先——recovery.c pass 驱动语义），
单个校验保持独立可调用。

## 验收标准

- [ ] AC-1: 修改前逐段记录 recovery pass 驱动与四个校验的源码/现状锚点。
- [ ] AC-2: verify_all() 按 拓扑→派生状态→桶索引→守卫 顺序全部执行，保留首个错误返回（对齐 `__bch2_run_explicit_recovery_pass(...) ?: ret` 模式），不改变单个校验行为。
- [ ] AC-3: 既有测试断言（29 处 verify_bucket_indexes + guard 调用）切换为 verify_all，全套测试保持绿。
- [ ] AC-4: 聚合入口自身有定向测试：单校验失败时 verify_all 返回该错误；多个校验同时失败时返回首个（顺序验证），且全部校验均执行（非短路）。
- [ ] AC-5: 属性测试逐 op 使用 verify_all（替换双校验调用点）。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- 顺序固定：verify → verify_derived_state → verify_bucket_indexes →
  verify_guard_invariants（对应 pass 依赖序：拓扑最基础，守卫最上层）。
- 全部执行、首个错误优先：每个校验都运行，返回首个 Err（`?:` 语义），
  不短路不吞错（recovery.c:68-98 逐 pass 执行并 `?: ret`）。
- 不新增校验逻辑；单个校验 API 保留（调用方可能只需局部校验）。

## 范围外

修复/repair 路径、新校验逻辑、pass 并行、真实设备 I/O、多设备拓扑。

## 备注

前置：T0189/T0191/T0192/T0193 已归档，四个校验均已对齐上游语义。
