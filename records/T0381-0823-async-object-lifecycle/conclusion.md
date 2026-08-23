---
schema: pdca.asset/v1
id: T0381-0823-async-object-lifecycle
phase: check
source_ids: [ac1-unified-post-contract, ac1-dual-axis-review, ac2-sanitizer-final, ac3-regression-final, ac4-baseline-comparison, ac5-task-tree-dag]
---

## 上下文

backupstream 异步基础设施所有权管理多套并存（8 个 post 变体、注释约定所有权、async_owned 布尔标志、generation 防 ABA），调用方心智负担高。任务按 ADR-0029 交付统一 C 风格生命周期契约：统一 owned-post 入口 + 守卫原语销毁栅栏，父任务完成核心原语与自迁移，业务 runtime 迁移归子任务 T0382-T0385。

## 假设与结果

- 假设 1：可在不引入智能指针/refcount 的前提下以显式契约达成强销毁保证 → 成立（guard 单原子字窗口原语 + post 所有权终态协议）。
- 假设 2：热路径近零开销可保持 → 成立且反向受益（合并消除双层转发，post 吞吐 +37%）。
- 假设 3：一次性替换可保绿执行 → 成立（expand 薄封装 + legacy 契约测试守护，121/121 回归绿）。

## 分析

- **AC-1** ✅ 统一守卫原语落地：reactor_post_submit 收敛五维度，enqueue_impl 合一双协议，work_pool/reactor_group 核心调用点自迁移，旧变体薄封装保留且有 expand 契约测试断言其存在与等价（ac1-unified-post-contract）
- **AC-2** ✅ 新增 reactor_lifecycle_stress 测试 9 项（派发恰好一次/abandon discard 恰好一次/失败保留所有权/WAIT 背压终态不变量/观测填充/guard 语义/销毁等待开启窗口/并发 guard×destroy 竞争/legacy 契约），ASan+UBSan 通过、TSan 连续 3 轮通过；TSan 曾暴露测试自身竞态已按终态不变量修复（ac2-sanitizer-final）
- **AC-3** ✅ 全量 ctest 121/121 绿，含 callback/work_pool 既有集成行为等价（ac3-regression-final）
- **AC-4** ✅ Release -O3 配对口径：reactor_post 吞吐中位 base 2.870→new 3.950 M/s（+37%），work_pool completion 中位比 0.998 持平；数据面热路径零新增分配/原子操作（ac4-baseline-comparison）
- **AC-5** ⏳ 部分——任务树 T0382-T0385 已创建、依赖登记且 DAG 三批次校验 valid（ac5-task-tree-dag）；"旧变体删除 grep=0"为收尾子任务 T0385 的交付条件，父任务按计划在全部子任务归档后方可收口归档

## 适用边界

- 本结论覆盖父任务（契约+核心原语+压力测试基建）。guard 原语尚未接入任何业务 runtime——业务侧 async_owned/force_destroy 收编是 T0382-T0385 的职责。
- 性能结论仅适用于 -O3 Release 口径；-O0 Debug 下合并函数曾现约 -40% 假回退，基准对照必须使用项目真实构建配置。
- 强销毁保证的"对象层"语义由 guard 原语提供机制能力，调用侧收益在迁移完成后兑现。

## 下一轮建议

1. 按批次调度 T0382/T0383（可并行）→ T0384 → T0385；每批迁移后跑全量 ctest 保绿。
2. T0385 删旧时收敛 source_kind 双处钳制与 priority↔flags 双向映射（审查遗留判断项）。
3. 后续可为 guard 原语增加 owner 线程亲和校验（对齐 tls_reactor 的 require_owner 模式），进一步消除跨线程误用。

## verdict

{"outcome": "confirmed", "reason": "AC-1~AC-4 全部通过证据支撑，AC-5 任务树就绪、收口归 T0385；双轴审查 Blocking=0，用户 verdict confirmed", "verdict_id": "T0381-check-confirmed-1", "at": "2026-08-23T21:40:05+08:00"}
