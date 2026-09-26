---
name: pdca-check
description: 用户明确启动现有 PDCA 任务的 Check 时使用。不修改业务对象或自动返工。
metadata:
  version: 5.0.0-rc.2
---

# Check：AI 直接审查事实与符合性

## 进入 Check

先执行[共同恢复入口](../../ontology/contracts/entry-recovery.md)。当前会话不是原任务执行者时，
只路由真实用户操作回原 Agent；不可路由就阻断。

必须绑定当前用户启动的 Check run、最新 Do 产物、固定 Plan/AC/oracle 和实际 subject 版本。
对象变化后旧 PASS/旧证据失效。读取[Check 方法](../../ontology/process/flow-check.md)、
当前 scene Skill 的“阶段方法”，其余规则按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 按需读取。

## 审查

严格按 flow-check 的四遍执行：

1. Scope Review；
2. Consistency Review；
3. Adversarial Review；
4. Evidence Review。

通用 Git、文本读取/搜索、格式解析、编译器、shell syntax check，以及 TARGET_ROOT 已有测试、
构建和静态分析只负责提供事实。不得新增项目专用 semantic validator 去重新编码 PDCA 规则；
权威冲突或证据不足保持 unknown/not_run。

需要第二视角时只使用一次性、只读、minimum sufficient context 的独立 AI review；
其输出是待核验 claim，不创建新 PDCA，也不替代正式 `pdca-verify`。

## 完成与停止

Finding 可使用 flow-check 定义的 BLOCKING / NON_BLOCKING / UNKNOWN；
最终 verdict 仍使用 EVIDENCE-01 / VERDICT-01 的既有语义。

保存证据、反证、限制和 verdict，向用户展示可选的 Act 或新 Do 方向后停止。
Check 不修改冻结业务对象、不自动返工，也不自动进入 Act。
