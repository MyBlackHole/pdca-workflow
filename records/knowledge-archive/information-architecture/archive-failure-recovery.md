---
schema: pdca.asset/v1
id: knowledge:information-architecture.archive-failure-recovery
layer: knowledge
summary: 归档流程通过边界故障注入验证 rollback、receipt 重放与 marker 归属保护
tags: [recovery, failpoint, archive, idempotency]
scenarios: [default, technical-design]
phases: [act]
applies_when: [需要测试归档跨目录、状态和 marker 的恢复一致性]
excludes_when: [需要操作系统级 kill 或真实磁盘损坏模拟]
source_ids: [experience:T0018--07-26-增加归档故障注入与恢复验证]
confidence: high
status: active
---

# Archive Failure Recovery Contract

归档流程应将关键持久化边界视为可恢复状态机：

1. rename 后失败必须把 archive 目录移回 live，并保持 Act 与 active marker。
2. archive task 保存后失败必须同时回滚目录和原 task 内容。
3. state 已切换到 `no_task` 后失败不能盲目回滚；应保留 archive receipt，让下一次
   Runtime Act 校验 receipt 后返回 `already_advanced`。
4. recovery 清理 active marker 前必须校验 marker 指向的 task 与 archived receipt 一致，
   指向其他任务时 fail-closed。

`PDCA_FAILPOINT` 只用于测试显式注入，默认环境不得改变归档顺序或行为。真实进程 kill 和
磁盘级故障仍需更底层设施验证。
