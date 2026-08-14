---
schema: pdca.asset/v1
id: T0261-0814-followup-task-record-identity
phase: check
source_ids: [identity-inventory, reproduction-results, solution-comparison, research-report, convergence-map]
---

## 上下文

T0260 发现 23 个 task ID 冲突和 5 条 event path mismatch。本任务不直接修复，而是用真实历史、当前代码路径、可执行并发复现和正常负对照，判断记录机制是否发现了真实问题，并为下一轮开发冻结可证伪方案。

## 假设与结果

| 假设 | 结果 |
|---|---|
| H1：普通 Plan 创建缺少统一原子 ID 分配，并发会选择同一 next ID | **supported（机制与可复现性）**：隔离并发创建实际产生两个 `T9001`；历史每个冲突的具体创建者仍 unknown。 |
| H2：promotion 是安全负对照 | **supported**：仓库既有并发测试通过，锁覆盖去重、分配与 create-only 写入。 |
| H3：mismatch 源于 record 生命周期变化或事件写入后归并 | **partial**：真实 transition 路径可稳定把同一 task 的事件写入两个 record identity；历史 T0252 的具体搬移命令没有 receipt。 |
| H4：task ID collision 是放大器，不是 mismatch 的充分原因 | **supported**：23 个冲突 ID 中 22 个没有 mismatch。 |

## 分析

### PRD 验收

AC-1 至 AC-8 均由已登记的非 convergence-map 证据覆盖；Do→Check 门禁与 `validate-convergence.py` 均通过。任务没有修改历史 task、record、occurrence 或正式 backlog。

### 自我审查是否有效

有效，但结论有边界。create-only occurrence 保留原始 payload，projection 又严格校验目录身份，因此 5 条 T0252 异常没有被汇总层吞掉。真实 `transition-phase.py` 复现进一步证明，这些异常对应当前可触发的设计缺陷：audit 在 `meta.record` 缺失时回退到 `task.id`，补 record 后又切换身份。

这也暴露记录方式自身的问题：非阻断 audit 在记录缺失时会制造第二身份，且系统没有 relocation receipt 表达合法归并。记录“能发现问题”与“记录实现无需改进”不能混为一谈。

### 推荐方案

采用组合方案，而不是二选一：所有任务入口统一进入仓库级原子创建事务；任务出生时分配不可变 record identity；audit 取消 `task.id` fallback；历史兼容只能通过绑定事件 digest 的 immutable relocation/alias receipt，禁止改写原始事件。开发必须先建立并发、身份不可变和路径一致性测试。

## 失败原因（仅 rejected/partial）

- Git 历史未保存 T0252 五条事件的目录归并命令、执行者或 relocation receipt，所以不能断言具体历史操作根因。
- instruction-driven 创建没有统一调用 receipt，23 个历史冲突只能按路径、时间和 commit 分类，不能逐个归责到某一命令或会话。
- 推荐方案尚未实施，也没有 14 天或 20 个真实任务的 post-change 数据，因此不能宣称效率或可靠性已经提升。

## 适用边界

- 并发复现证明当前 scan→create 模式不安全，不证明所有历史冲突都由并发产生；复制、迁移或多分支也可能造成同样结果。
- 真实 transition 复现证明身份分裂机制存在，不证明历史文件一定由同一工具搬移。
- 当前基线是冻结时的 23 个冲突 ID、47 个不同 slug、49 份物理 task 和 5 条 mismatch；工作区继续产生任务后数字可能变化。

## 下一轮建议

创建独立 development 跟进任务，按 `solution-comparison` 的 paired seam 先写失败测试，再实现统一创建事务与不可变 record identity。观察窗口达到 14 天或 20 个真实新任务后，必须回到真实记录评估 duplicate ID、missing record、path mismatch、创建失败和人工恢复次数，才可给 effectiveness verdict。
