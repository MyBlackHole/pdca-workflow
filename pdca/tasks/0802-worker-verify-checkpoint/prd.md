# T0196 worker 变体最终一致性检查点

## 问题陈述

discard worker（T0190/T0191）与 reclaim worker 维护桶索引/派生状态
（freespace、need_discard、journal 回收），但运行后从未经过 verify_all
全量一致性校验（T0194 聚合入口已就绪）。worker 变体缺乏"运行后引擎仍
一致"的验证矩阵；T0191 建议的「run 后队列空不变量公开断言」已由 T0193
的 `discard_queue_empty` 提供，但未与 verify_all 组合成 worker 生命周期
检查点。

## 目标

为 discard/reclaim worker 生命周期建立测试级最终一致性检查点：
worker 运行后运行 verify_all + discard_queue_empty，覆盖正常、
并发、EAGAIN 旋转、not_rw 设备与非法态场景。不新增公开 API
（约束 8：上游无"worker 后自动 verify"函数）。

## 验收标准

- [ ] AC-1: 修改前逐段记录上游锚点：discard.c:598-633 fast_work 循环、
      journal/reclaim.c、alloc/check.c:323-345 freespace 校验与 worker
      维护状态的验证关系。
- [ ] AC-2: discard worker 正常路径（队列 drain 空）后 verify_all 通过且
      discard_queue_empty 为真，含并发入队场景（既有 FIFO 测试叠加
      verify_all）。
- [ ] AC-3: discard worker 边界路径后一致性正确：EAGAIN 旋转（桶延迟但
      队列非空是合法状态）verify_all 仍通过；not_rw 设备 free 桶非法态下
      worker 跳过、verify_all 报对应错误（既有非法态语义保留）。
- [ ] AC-4: reclaim worker：request_reclaim 触发 checkpoint 完成后
      verify_all 通过（journal 状态恢复后一致性）。
- [ ] AC-5: 库 API 不变（检查点为测试级；复用 discard_queue_empty /
      verify_all 既有公开 API）。
- [ ] AC-6: workspace 全量测试、fmt、diff gate 通过，单项不超过一分钟。

## 实现决策

- 检查点为测试级断言模式（新测试不新增生产代码或仅新增内部辅助），
  生产路径零改动或最小改动。
- 复用既有测试基础设施：prepared_bucket_engine、add_free_bucket、
  set_need_discard_index（内部辅助）。
- 非法态场景保留既有断言语义（not_rw free 桶 = verify 必然失败），
  不在检查点矩阵中强制通过。

## 范围外

真实 TRIM、GC/LRU、-f force 修复路径、worker 钩子 API、
loom 风格并发模型。

## 备注

前置：T0190/T0191（discard worker）、T0193（公开断言）、T0194
（verify_all 聚合）、T0195（fsck_image）已归档。
