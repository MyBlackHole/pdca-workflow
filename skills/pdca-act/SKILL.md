---
name: pdca-act
description: 用户明确批准现有 PDCA 任务的 Act 处置时使用。不启动下一场景。
metadata:
  version: 5.0.0-rc.2
---

# Act：执行已批准处置并封存真实结果

## 进入 Act

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。当前会话不是原任务执行者时，
只路由真实用户操作回原 Agent；不可路由就阻断。

当前用户操作必须明确对应当前 Check 报告、产物版本和具体处置范围。
读取[Act 方法](../../ontology/process/flow-act.md)和当前 scene Skill 的“阶段方法”；
资源、发布、知识采用等规则按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的实际事件读取。

## 本阶段动作

只执行用户这次明确批准的处置，例如接受交付、失败/unknown 归档、返工安排、局部经验固定或共享发布。
“同意”“可以”之类未绑定对象和范围的回应不能扩大成其他写入、发布或知识更新。

复盘、经验、项目上下文或共享 ontology 的额外写入不是 Act 默认副作用。
只有用户此次明确包含对应对象、写域和处置时才执行；否则只报告可选项，不为了“完整复盘”自动新增记录。

保留 Check 的真实结论：fail/unknown 可以被诚实归档，但不能因此变成 PASS 或
`delivery_usable=true`。结清或明确 retained 的实际资源；未知业务结果先对账，不重复发布或归还。

## 完成与停止

固定最终交付、模型/mapping/implementation 版本、处置证据、资源结果和实际 scene coverage，
保存 `phase_completed` 与 `archived`，报告未决事项后停止。

Act 不自动创建 child、启动下一 scene、新 attempt 或第五阶段。
