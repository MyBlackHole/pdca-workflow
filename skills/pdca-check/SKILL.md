---
name: pdca-check
description: 用户明确启动现有 PDCA 任务的 Check 时使用。核验固定产物、标准和证据，在原会话完成，不修改业务对象或自动返工。
metadata:
  version: 4.0.0-rc.2
---

# Check：核验事实，不自动修正业务对象

## 先定位，不以加载当授权

安装后的入口会给出真实 **PDCA_ROOT** 和当前发布快照。直接从源码读取时，由用户明确集中根，或核对该文件真实路径所在的根；定位不等于批准业务操作。路径冲突时停止，不在目标项目创建 `.pdca/` 或另一份 records。

先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)，再读集中项目 context、自己的 task/原 Agent 绑定、最后完整事件和当前请求。已有任务采用 `protocol_baseline_ref` 所在快照；与本入口版本或摘要不同，则只作定位并读取原快照方法，不用这里的新方法推进旧任务。

当前会话不是该任务执行者时，只把真实用户操作路由回原 Agent 后停止本地执行；不可路由就阻断。**切换 Skill 不换 Agent**，不要调用新建工具、设置自动 fork 或由父 Agent 接管。加载方法、文件存在和上一阶段 PASS 都不授权本阶段。

开始前核对匹配 task/attempt/phase/run/subject 的原始用户回应、固定输入及撤权状态，并核验集中资源预约及实际写权。缺项时展示本阶段目标和缺项后等待；已有明确确认不要重复盘问。无任务时返回总入口定位，不在阶段 Skill 中新建。

## 当前 run 的动作

1. 锁定最新 Do run 的需求、模型、目标产物、映射与 AC/oracle；旧 PASS 不能用于新字节。读取[Check 方法](../../ontology/process/flow-check.md)及当前场景方法。
2. 逐项核对对象→实际执行→actual/expected→反证→结论。命令退出 0 不证明业务符合；缺模型、映射或必需运行事实就列缺项，不缩小标准。
3. 追踪可疑路径和上游保护、源与投影的双向覆盖，区分确定违例、unknown和纯建议。没有证据不能编造“已验证”；不能靠多个模型赞同提升为事实。
4. 不修改冻结业务对象、模型目标和oracle。测试环境/夹具修复仅限本次已批准写域，保留前后证据并保持被审对象与预期不变；否则停止沟通。
5. 当 task.scene=ontology_conformance_verification，本 Check 验证 Do 的检查过程、报告和证据是否可靠，不递归创建新的审查 Agent 或无限检查自身。

## 报告与停止

分别报告任务执行是否完整、对象 pass/fail/unknown、交付是否可用。保存报告并提出 Act 处置或新 Do 返修选项，随后等待。用户认可不使 fail 变 PASS，Check 不自动返工。
