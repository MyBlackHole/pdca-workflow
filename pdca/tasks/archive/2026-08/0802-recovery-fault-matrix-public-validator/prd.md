# T0186 公开派生状态校验 API 与 recovery fault matrix

## 问题陈述

T0185 已实现 alloc/backpointer 派生集合校验，并在 journal replay 与 persistent recovery 的
rebuild 后执行校验。但当前校验器仍是内部函数，错误只映射为通用 transaction error；fault
注入也只覆盖 transaction restart 与 journal write，无法独立观察 recovery 中间阶段的发布边界。

本任务依据本地 bcachefs `fs/init/recovery.c` 的 explicit recovery passes、
`fs/alloc/backpointers.c` 的双向 mismatch 检查，以及现有 subvol journal/recovery 控制流，
不引入完整 fsck 或 allocator 行为。

## 目标

1. 为 `StorageEngine` 提供只读派生状态校验入口，返回可定位的结构化 mismatch。
2. 将 recovery 的 journal durable、derived rebuild、publication 前边界建模为 deterministic
   fault points。
3. 对每个 fault point 执行 crash/restart/validator 闭环，并用属性测试覆盖随机 pointer 序列。

## 验收标准

- [ ] AC-1: 修改前重新读取并记录本地 `recovery.c`、`backpointers.c` 对应 explicit pass、
  mismatch 和错误传播分支；实现中的每个 fault/错误分支均有源码锚点。
- [ ] AC-2: 提供公开只读派生校验 API；正常 primary/alloc/backpointer 状态通过，missing、
  duplicate、generation、bucket、owner mismatch 返回稳定且可定位的结构化结果。
- [ ] AC-3: 新增 recovery fault points，分别覆盖 journal durable 后、derived rebuild 中、
  publication 前；fault 后不得把不完整派生状态作为成功恢复结果发布。
- [ ] AC-4: 每个 fault point 都有 deterministic restart 测试；重启后主记录 replay、derived
  rebuild、validator 顺序正确，最终状态与无 fault 基线一致。
- [ ] AC-5: pointer 属性测试、全量 workspace 测试、`cargo fmt --check` 和 diff gate 全部通过；
  每项测试不超过一分钟。

## 实现决策

- 复用 T0185 的 primary authority、集合比较和 members-v2 geometry，不创建新持久化格式。
- 结构化 mismatch 只描述检测结果，不在校验 API 中隐式修复数据。
- fault 注入必须绑定现有 recovery 控制流；不得新增无本地 bcachefs 语义依据的恢复分支。
- publication 只有在 replay、rebuild、validator 全部成功后才返回成功。

## 测试决策

- 先覆盖公开 validator 的正常与 corruption seam，再覆盖三个 recovery fault phase。
- 使用 durable journal snapshot 作为 crash 边界，对照无 fault 基线比较 primary 和派生集合。
- 属性测试生成 insert/overwrite/delete/interior pointer 序列，并在 fault 点重启。

## 范围外

完整 device allocator、GC、LRU/discard、stripe/EC、完整 fsck、VFS、旧格式迁移和多格式兼容。

## 备注

前置：T0185 已完成并归档。T0183 已被 T0182 吸收，不重新启用。
