# T0185 实现 alloc/backpointer 派生状态校验与故障恢复闭环

## 问题陈述

T0182 已完成 physical pointer 的 transaction trigger、alloc/backpointer 派生写入、journal
replay 和 deterministic rebuild。当前仍缺少一个独立、可重复调用的校验器，能够将主 pointer
记录与派生 alloc/backpointer 集合逐项比较，并覆盖派生重建及 publication 边界的故障恢复。

本任务仅依据本地 bcachefs 源码：`fs/init/recovery.c` 的 recovery check passes、
`fs/alloc/backpointers.c` 的 extent-to-backpointer mismatch 检查，以及
`fs/alloc/background.c` 的 alloc key 校验/重建路径。不得扩大到完整 allocator、GC 或 fsck。

## 目标

1. 建立独立 validator，从主 extent、btree pointer、btree pointer v2 扫描结果推导期望的
   alloc/backpointer 集合，并与持久化派生树比较。
2. 明确报告 missing、duplicate、stale generation、错误 bucket/owner 等 mismatch。
3. 覆盖 journal durable、derived rebuild、publication 前后的 deterministic fault/restart，
   保证恢复完成前不发布不完整派生状态。
4. 用故障测试和属性测试证明恢复后的主/派生集合最终一致。

## 验收标准

- [ ] AC-1: 修改前读取并记录本地 `fs/init/recovery.c`、`fs/alloc/backpointers.c`、
  `fs/alloc/background.c` 对应检查/重建分支；每个 validator 与 recovery 分支有源码锚点。
- [ ] AC-2: validator 独立扫描主 pointer，并逐项比较 alloc/backpointer；能稳定识别 missing、
  duplicate、stale generation、错误 bucket/owner，并返回可定位的 mismatch。
- [ ] AC-3: 正常 insert、overwrite、delete、interior pointer 更新及 rebuild 后，validator
  均通过；故意删除、复制或修改派生记录时，validator 必须失败且不改变数据。
- [ ] AC-4: 在 journal durable 后派生更新前、rebuild 中、publication 前注入 fault/restart；
  重启后先完成主记录 replay，再完成派生 rebuild/校验，完成前不得观察到不完整派生状态。
- [ ] AC-5: 定向测试、故障注入测试、属性测试和全量 workspace 测试通过；每项测试不超过一分钟，
  `cargo fmt --check` 与 diff gate 通过。

## 实现决策

- 复用 T0182 已有 pointer、alloc、backpointer、journal 和 recovery 数据结构，不创建新的
  持久化格式或 allocator 策略。
- validator 作为只读检查路径；不得在校验失败时隐式修复、删除或重写记录。
- publication gate 只表达 recovery 状态，不开放 alloc 查询、GC、LRU 或 stripe 行为。
- 故障点必须对应现有 journal/recovery 控制流，并通过可重复测试验证，禁止引入无 bcachefs
  语义依据的额外恢复分支。

## 测试决策

- 先添加单条/多条 pointer 的集合等价测试，再覆盖 overwrite/delete/interior 更新。
- 对每个故障点执行崩溃、重启、validator 三段式检查。
- 属性测试生成有效 pointer 变更序列，并在随机 fault 点重启后比较主/派生集合。

## 范围外

完整 device allocator、open bucket、free-index、LRU/discard、GC、stripe/EC、完整 fsck、
VFS、旧格式迁移和多格式兼容。

## 备注

前置：T0182 已完成。原 T0183 的写入与恢复范围已被 T0182 吸收；T0183 不进入 Do，保留为
历史 Plan 任务处理。
