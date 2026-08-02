# T0194 结论

## 概述

verify_all 聚合入口：按 拓扑→派生状态→桶索引→守卫 依赖序执行全部四个
一致性校验，全部执行、首个错误优先（对齐 recovery.c `?:` 模式）。35 处
既有断言切换，3 个新定向测试验证单/多校验失败顺序。

## 验证

- workspace：211 lib + 10 集成全绿（10.19s/38.34s，≤1min）
- fmt 通过；diff +136/-32 单文件
- 双轴审查：0 blocking / 0 MEDIUM / 0 LOW

## 边界与发现

- not_rw 设备上 free 桶是测试故意构造的非法态：verify_all 在该态必然
  失败（守卫语义），`discard_worker_requires_rw_device` 保留
  verify_bucket_indexes 单校验（正确，非缺陷）。
- 聚合入口复用既有错误类型与锁序，无新变体；live btree 快照在局部作用域
  获取，不跨校验持锁。
- 属性测试逐 op 使用 verify_all，覆盖全部四个校验。

## 下一轮建议

1. 将 verify_all 作为引擎公开 API 的"健康检查"入口，暴露到 CLI/诊断层
   （当前为库 API）。
2. worker 变体（T0191 建议）在 run 后调用 verify_all 作为最终一致性
   检查点。
3. 属性测试模型状态机直接注入守卫决策（T0193 建议延续），消除模型与
   实现间的重复校验。
