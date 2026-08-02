# T0188 Triage Brief

## 分类

- 类型：enhancement
- 场景：development
- 父任务：T0187

## 查重与事实核验

- T0187 已完成最小 bucket allocation/reclaim/backpointer/recovery 核心。
- 当前实现已有底层 transaction 状态序列测试，但公开 `allocate_bucket`/
  `reclaim_bucket` 的端到端模型和属性覆盖不足。
- T0183 是旧的派生维护任务，已被 T0182/T0185/T0186/T0187 的实现吸收，不重复开启。

## 推荐

先补公开 API 的确定性、故障注入和属性测试，再考虑完整 discard worker/open-bucket GC。
